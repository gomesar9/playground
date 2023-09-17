mod models;


fn main() {
    println!("Lets create some User!");

    let user = models::User::new("John".to_string(), "john@gmail.com".to_string()).build();

    println!("User: {:?}", user);
}
