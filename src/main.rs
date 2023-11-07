use async_openai;
use async_openai::types::{
    ChatCompletionRequestMessageArgs, CreateChatCompletionRequestArgs, CreateEmbeddingRequest, Role,
};
use duckdb::*;
use feed_rs::{model, parser};
use reqwest;
use serde::{Deserialize, Serialize};
use soup::Soup;
use tokio;
mod db;
use serde_json::{json, to_string_pretty};
use std::collections::HashMap;
use std::fs::File;
use std::io::Write;

#[derive(Serialize, Deserialize)]
struct Emotions {
    #[serde(default)]
    anger: f32,
    #[serde(default)]
    anticipation: f32,
    #[serde(default)]
    joy: f32,
    #[serde(default)]
    trust: f32,
    #[serde(default)]
    fear: f32,
    #[serde(default)]
    surprise: f32,
    #[serde(default)]
    sadness: f32,
    #[serde(default)]
    disgust: f32,
}

#[derive(Serialize, Deserialize)]
struct NewsEmoticon {
    guid: String,

    #[serde(skip_serializing)]
    published_date: String,

    emoticon: String,
}

async fn update_items(connection: &Connection) -> () {
    // Step 1: Download the RSS feed
    let feed_url = "https://feeds.nos.nl/nosnieuwsalgemeen";
    let response = reqwest::Client::new().get(feed_url).send().await.unwrap();
    let body = response.text().await.unwrap();
    let channel = parser::parse(body.as_bytes()).unwrap();

    for item in channel.entries {
        //Extract guid, title and description from entry
        // dbg!(item);
        let guid = item.id;
        let title = item.title.unwrap().content;
        let description = Soup::new(
            // format!("<body>{}</body>", item.summary.unwrap().content).as_str(),
            item.summary.unwrap().content.as_str(),
        )
        .text();
        connection
            .execute(
                "insert or ignore into news_items values (?,?,?,?)",
                params![
                    guid,
                    item.published.unwrap().format("%Y-%m-%d").to_string(),
                    title,
                    description
                ],
            )
            .expect("Failed to insert item");
    }
}

async fn load_emoticon(connection: &Connection, guid: &str) -> () {
    let mut stmt = connection
        .prepare("select description from news_items where guid = ?")
        .unwrap();
    let news_item: String = stmt
        .query(params![guid])
        .unwrap()
        .next()
        .unwrap()
        .unwrap()
        .get(0)
        .unwrap();
    
    let client = async_openai::Client::new();

    let request = CreateChatCompletionRequestArgs::default()
        .max_tokens(512u16)
        .model("gpt-3.5-turbo")
        .messages([
            ChatCompletionRequestMessageArgs::default()
                .role(Role::System)
                .content("Geef de best passende, enkele, emoticon voor ontvangen bericht")
                .build()
                .unwrap(),
            ChatCompletionRequestMessageArgs::default()
                .role(Role::User)
                .content(news_item)
                .build()
                .unwrap(),
        ])
        .build()
        .unwrap();
    let response = client.chat().create(request).await.unwrap();
    let choice = response.choices.first().unwrap().clone();
    let json_response = choice.message.content.unwrap();
    connection
        .execute(
            "insert or ignore into chat_responses(guid, response_content) values (?,?)",
            params![guid, json_response],
        )
        .expect(format!("Failed to insert response for {guid}").as_str());
    ()
}

#[tokio::main]
async fn main() {
    // Open and initialize database
    let connection = Connection::open("data/nos_algemeen.duckdb").expect("Failed to open database");
    db::create_tables(&connection).await;

    update_items(&connection).await;

    // Fetch guids that have not run through chatgpt yet
    let mut stmt = connection
        .prepare("select guid from news_items anti join chat_responses using (guid)")
        .unwrap();
    let missing_chats_iter = stmt
        .query_map([], |row| {
            let v: String = row.get(0).unwrap();
            Ok(v)
        })
        .unwrap();

    for guid_result in missing_chats_iter {
        let guid = guid_result.unwrap();
        println!("Loading guid {}", guid);
        load_emoticon(&connection, &guid).await;
    }

    // Fetch all the emotions from the database and put them in a json file
    let mut stmt = connection
        .prepare(
            "select guid, strftime(published_date, '%x'), response_content from news_items inner join chat_responses using (guid)",
        )
        .unwrap();

    let emoticons_iter = stmt
        .query_map([], |row| {
            Ok(NewsEmoticon {
                guid: row.get(0).unwrap(),
                published_date: row.get(1).unwrap(),
                emoticon: row.get(2).unwrap(),
            })
        })
        .unwrap();

    // Create a HashMap to group items by published_date
    let mut grouped_items: HashMap<String, Vec<NewsEmoticon>> = HashMap::new();

    for item_result in emoticons_iter {
        match item_result {
            Ok(item) => {
                grouped_items
                    .entry(item.published_date.clone())
                    .or_insert_with(Vec::new)
                    .push(item);
            }
            Err(e) => panic!("Error: {}", e),
        }
    }

    // Write each group into a json file
    for (published_date, items) in grouped_items {
        let json_data = json!(items);
        let json_string = to_string_pretty(&json_data).expect("Failed to convert to JSON string");

        let file_name = format!("public/data/{}.json", published_date);

        let mut file = File::create(file_name).expect("Failed to create file");
        file.write_all(json_string.as_bytes())
            .expect("Failed to write to file");
    }

    ()
}
