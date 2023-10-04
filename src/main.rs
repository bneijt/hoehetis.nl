use async_openai;
use async_openai::types::{
    ChatCompletionRequestMessageArgs, CreateChatCompletionRequestArgs, Role,
};
use duckdb::*;
use feed_rs::parser;
use reqwest;
use soup::Soup;
use tokio;

async fn update_items(connection: &Connection) -> () {
    // Step 1: Download the RSS feed
    let feed_url = "https://feeds.nos.nl/nosnieuwsalgemeen";
    let response = reqwest::Client::new().get(feed_url).send().await.unwrap();
    let body = response.text().await.unwrap();
    let channel = parser::parse(body.as_bytes()).unwrap();

    connection
        .execute(
            "create table  if not exists news_items(
                    guid varchar primary key,
                    published_date date,
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

#[tokio::main]
async fn main() {
    // Open and initialize database
    let connection = Connection::open("data/nos_algemeen.duckdb").expect("Failed to open database");
    update_items(&connection).await;
    connection
        .execute(
            "create table  if not exists emotions(
                    guid varchar primary key,
                    anger float,
                    anticipation float,
                    joy float,
                    trust float,
                    fear float,
                    surprise float,
                    sadness float,
                    disgust float
                )",
            params![],
        )
        .expect("Failed to create table");

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
                .content(r###"Er was nog weinig twijfel over, maar nu is er het definitieve bewijs dat prins Bernhard lid was van de NSDAP, de partij van Adolf Hitler. De originele NSDAP-lidmaatschapskaart is in het archief van de prins gevonden.In zijn boek De Achterblijvers, dat deze woensdag verschijnt, onthult Flip Maarschalkerweerd dat hij de originele NSDAP-lidmaatschapskaart van de prins heeft gevonden, schrijft NRC. Maarschalkerweerd is oud-directeur van het Koninklijk Huisarchief. Hij vond de kaart op paleis Soestdijk in het privéarchief van de prins dat hij na diens overlijden in 2004 moest inventariseren.Tot zijn dood ontkendPrins Bernhard heeft tot aan zijn dood ontkend dat hij lid was van de nazipartij. Ook toen hij met eerder bewijs werd geconfronteerd. In 1996 meldden historici al dat ze een kopie van zijn lidmaatschapskaart gevonden hadden in de VS. Ook werd er correspondentie over de opzegging van lidmaatschap uit 1936 gevonden. In dat jaar verloofde hij zich met Juliana. Bernhard gaf alleen toe dat hij een tijd lid was geweest van een afdeling van de SS.Prins BernardPrins Bernhard (1911-2004), geboren in Duitsland, was de man van prinses Juliana, de vader van prinses Beatrix en opa van koning Willem-Alexander. Tijdens de oorlog vluchtte hij met Juliana naar Londen. Aan het einde van de oorlog werd hij door koningin Wilhelmina benoemd tot bevelhebber van de Binnenlandse Strijdkrachten, waar verschillende verzetsgroepen onder vielen.In een serie vraaggesprekken die hij voor zijn dood had met de Volkskrant zei de prins nog: "Ik kan met de hand op de Bijbel verklaren: ik was nooit een nazi. Ik heb nooit het partijlidmaatschap betaald, ik heb nooit een lidmaatschapskaart gehad."'Spectaculaire vondst'Historica en schrijfster Annejet van der Zijl, die het boek al heeft gelezen, noemt de vondst "spectaculair". "Echt mooi dat 100 procent de historische waarheid is komen bovendrijven. Dat is een pluim waard voor Maarschalkerweerd en voor de koninklijke familie, die toelaat dat dit openbaar wordt", zegt ze in het NOS Radio 1 Journaal. Van der Zijl schreef in 2010 een boek over Bernhard, waarin ze onthulde dat hij lid was geweest van een nationaalsocialistische studentenvereniging. Ook stond er op de lidmaatschapskaart van die vereniging een aantekening dat hij lid was van de NSDAP.Het verbaast Van der Zijl dat Bernhard de lidmaatschapskaart niet heeft verbrand. "Er zijn genoeg open haarden op Soestdijk, lijkt mij. Ik kan niet anders concluderen dan dat hij toch wel hechtte aan die periode in zijn leven", zegt ze. "Hij is ook altijd heel trouw gebleven aan vrienden uit die tijd die overtuigd nazi's waren en heeft altijd de vriendschap onderhouden."Volgens de historica heeft Bernhard nooit ingezien "hoe verwerpelijk het was". "Maar hij kon er ook niet mee naar buiten komen, want hij stond elk jaar weer op de Dam met allemaal leiders van Joodse belangenverenigingen vroom een krans te leggen voor de Dodenherdenking. En hij was de leider van het verzet. Het is een heel gespleten leven wat deze man heeft gehad."###)
                .build()
                .unwrap(),
        ])
        .build()
        .unwrap();
    let response = client.chat().create(request).await.unwrap();
    println!("\nResponse:\n");
    for choice in response.choices {
        println!(
            "{}: Role: {}  Content: {:?}",
            choice.index, choice.message.role, choice.message.content
        );
    }

    // {
    //     "id": "chatcmpl-123",
    //     "object": "chat.completion",
    //     "created": 1677652288,
    //     "model": "gpt-3.5-turbo-0613",
    //     "choices": [{
    //       "index": 0,
    //       "message": {
    //         "role": "assistant",
    //         "content": "\n\nHello there, how may I assist you today?",
    //       },
    //       "finish_reason": "stop"
    //     }],
    //     "usage": {
    //       "prompt_tokens": 9,
    //       "completion_tokens": 12,
    //       "total_tokens": 21
    //     }
    //   }

    // let api_key = "YOUR_API_KEY"; // Replace with your OpenAI API key
    // let prompt = "how are you?";
    // let endpoint = "https://api.openai.com/v1/chat/completions";

    // let client = reqwest::Client::new();
    // let response = client
    //     .post(endpoint)
    //     .header("Authorization", format!("Bearer {}", api_key))
    //     .json(&json!({
    //         "model": "gpt-3.5-turbo",
    //         "messages": [
    //             {"role": "system", "content": "You are a helpful assistant."},
    //             {"role": "user", "content": prompt}
    //         ]
    //     }))
    //     .send()
    //     .await?;

    // let json_response: Value = response.json().await?;
    // let choices = &json_response["choices"][0]["message"]["content"];

    // println!("Response: {}", choices);

    ()
}
