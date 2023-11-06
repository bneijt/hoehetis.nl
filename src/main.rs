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

use canyon_sql::macros::canyon_entity;

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

/// Load the given guid content into emotions from chat_gpt
async fn load_emotions(connection: &Connection, guid: &str) -> () {
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
                .content("You are a JSON API giving out 0 to 1 scores with three decimals on eight emotional attributes: anger, anticipation, joy, trust, fear, surprise, sadness and disgust. You should give higher scores if the emotion better fits the contents and only respond with JSON containing those attributes.")
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
    // Parse response message as json and insert into database
    let emotions: Emotions = serde_json::from_str(&json_response).unwrap();
    connection
        .execute(
            "insert or ignore into emotions(guid, anger, anticipation, joy, trust, fear, surprise, sadness, disgust) values (?,?,?,?,?,?,?,?,?)",
            params![guid, emotions.anger,
            emotions.anticipation,
            emotions.joy,
            emotions.trust,
            emotions.fear,
            emotions.surprise,
            emotions.sadness,
            emotions.disgust],
        )
        .expect(format!("Failed to insert response for {guid}").as_str());
    ()
}

async fn embed(body: &str) -> Vec<f32> {
    let client = async_openai::Client::new();

    let request = CreateEmbeddingRequest {
        model: "text-embedding-ada-002".to_string(),
        input: body.into(),
        user: Some(String::from("hoehetis"))
    };

    let response = client.embeddings().create(request).await.unwrap();
    response.data.first().unwrap().embedding.clone()
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
        load_emotions(&connection, &guid).await;
    }
    ()
}
