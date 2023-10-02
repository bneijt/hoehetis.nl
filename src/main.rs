use feed_rs::parser;
use reqwest::Client;
use serde::{Deserialize, Serialize};
use surrealdb::engine::remote::ws::Ws;
// use surrealdb::opt::auth::Root;
use surrealdb::sql::Thing;
use surrealdb::Surreal;
use tokio;

#[derive(Debug, Deserialize)]
struct Record {
    #[allow(dead_code)]
    id: Thing,
}


#[derive(Debug, Serialize)]
struct RssItem {
    guid: String,
    title: String,
    description: String,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Step 1: Download the RSS feed
    let feed_url = "https://feeds.nos.nl/nosnieuwsalgemeen";
    let response = Client::new().get(feed_url).send().await?;
    let body = response.text().await?;
    let channel = parser::parse(body.as_bytes()).unwrap();

    // Step 2: Extract data and write to SurrealDB
    let surreal_db_url = "localhost:8000"; // Replace with your SurrealDB URL
    let db = Surreal::new::<Ws>(surreal_db_url).await?;
    // db.signin(Root {
    //     username: "root",
    //     password: "root",
    // })
    // .await?;
    db.use_ns("hoehetis").use_db("nos_algemeen").await?;

    for item in channel.entries {
        //Extract guid, title and description from entry
        // dbg!(item);
        let rss_item = RssItem {
            guid: item.id,
            title: item.title.unwrap().content,
            description: item.summary.unwrap().content,
        };

        let created: Vec<Record> = db.create("items").content(rss_item).await?;
        dbg!(created);
    }

    Ok(())
}
