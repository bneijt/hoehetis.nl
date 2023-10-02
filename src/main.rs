use duckdb::*;
use feed_rs::parser;
use reqwest::Client;
use soup::Soup;
use tokio;

async fn update_items(connection: Connection) -> () {
    // Step 1: Download the RSS feed
    let feed_url = "https://feeds.nos.nl/nosnieuwsalgemeen";
    let response = Client::new().get(feed_url).send().await.unwrap();
    let body = response.text().await.unwrap();
    let channel = parser::parse(body.as_bytes()).unwrap();

    connection
        .execute(
            "create table  if not exists news_items(
                    guid varchar primary key,
                    title varchar,
                    description varchar
                )",
            params![],
        )
        .expect("Failed to create table");

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
                "insert or ignore into news_items values (?,?,?)",
                params![guid, title, description],
            )
            .expect("Failed to insert item");
    }
}

#[tokio::main]
async fn main() {
    // Open and initialize database
    let connection = Connection::open("data/nos_algemeen.duckdb").expect("Failed to open database");
    update_items(connection).await;
    ()
}
