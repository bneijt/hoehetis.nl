use duckdb::*;
use feed_rs::parser;
use reqwest::Client;
use serde::{Deserialize, Serialize};
use soup::Soup;
use tokio;

#[derive(Debug, Deserialize, Serialize)]
struct RssItem {
    guid: String,
    title: String,
    description: String,
}

#[tokio::main]
async fn main() {
    // Step 1: Download the RSS feed
    let feed_url = "https://feeds.nos.nl/nosnieuwsalgemeen";
    let response = Client::new().get(feed_url).send().await.unwrap();
    let body = response.text().await.unwrap();
    let channel = parser::parse(body.as_bytes()).unwrap();

    // Open and initialize database
    let connection = Connection::open("data/nos_algemeen.duckdb").expect("Failed to open database");

    connection
        .execute(
            "CREATE TABLE  IF NOT EXISTS news_items (
                    guid VARCHAR  PRIMARY KEY,
                    title VARCHAR,
                    description VARCHAR
                )",
            params![],
        )
        .expect("Failed to create table");

    for item in channel.entries {
        //Extract guid, title and description from entry
        // dbg!(item);
        let rss_item = RssItem {
            guid: item.id,
            title: item.title.unwrap().content,
            description: Soup::new(
                // format!("<body>{}</body>", item.summary.unwrap().content).as_str(),
                item.summary.unwrap().content.as_str(),
            )
            .text(),
        };
        connection
            .execute(
                "INSERT OR IGNORE INTO news_items VALUES (?,?,?)",
                params![rss_item.guid, rss_item.title, rss_item.description],
            )
            .expect("Failed to insert item");
    }
    ()
}
