use duckdb::*;

pub async fn create_tables(connection: &duckdb::Connection) -> () {
    connection
        .execute(
            "create table if not exists news_items(
                guid varchar primary key,
                published_date date,
                published_timestamp integer,
                title varchar,
                description varchar
            )",
            params![],
        )
        .expect("Failed to create news_items table");
    connection
        .execute(
            "create table  if not exists chat_responses(
                    guid varchar primary key,
                    response_content varchar
                )",
            params![],
        )
        .expect("Failed to create chat_responses table");
    // connection
    //     .execute(
    //         "create table  if not exists emotions(
    //                 guid varchar primary key,
    //                 anger float,
    //                 anticipation float,
    //                 joy float,
    //                 trust float,
    //                 fear float,
    //                 surprise float,
    //                 sadness float,
    //                 disgust float
    //             )",
    //         params![],
    //     )
    //     .expect("Failed to create emotions table");

    ()
}
