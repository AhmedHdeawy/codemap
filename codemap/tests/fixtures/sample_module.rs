//! Sample Rust module for testing.

use std::error::Error;

/// Represents a user in the system.
pub struct User {
    pub id: u32,
    pub name: String,
}

/// Service trait for user operations.
pub trait UserService {
    fn get_user(&self, id: u32) -> Option<&User>;
    fn create_user(&mut self, name: String) -> &User;
}

/// User status enumeration.
pub enum UserStatus {
    Active,
    Inactive,
    Pending,
}

/// Implementation block for User.
impl User {
    /// Creates a new user.
    pub fn new(id: u32, name: String) -> Self {
        User { id, name }
    }

    /// Gets the display name.
    pub fn display_name(&self) -> String {
        format!("User: {}", self.name)
    }
}

/// Default service implementation.
pub struct DefaultService {
    users: Vec<User>,
}

impl UserService for DefaultService {
    fn get_user(&self, id: u32) -> Option<&User> {
        self.users.iter().find(|u| u.id == id)
    }

    fn create_user(&mut self, name: String) -> &User {
        let id = self.users.len() as u32 + 1;
        self.users.push(User::new(id, name));
        self.users.last().unwrap()
    }
}

/// Greets a user by name.
pub fn greet(name: &str) -> String {
    format!("Hello, {}!", name)
}

/// Async function for processing data.
pub async fn process_data(data: Vec<u8>) -> Result<Vec<u8>, Box<dyn Error>> {
    Ok(data)
}

/// Submodule for utilities.
pub mod utils {
    /// Formats a number.
    pub fn format_number(n: u32) -> String {
        n.to_string()
    }
}
