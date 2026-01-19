import 'dart:async';

/// Represents a user in the system.
class User {
  final int id;
  final String name;
  String? email;

  /// Creates a new user with ID and name.
  User(this.id, this.name);

  /// Creates a user from JSON data.
  User.fromJson(Map<String, dynamic> json)
      : id = json['id'],
        name = json['name'],
        email = json['email'];

  /// Factory constructor for creating guest users.
  factory User.guest() {
    return User(0, 'Guest');
  }

  /// Gets the display name.
  String getDisplayName() {
    return '$name (#$id)';
  }

  /// Checks if user is valid.
  bool isValid() {
    return id > 0 && name.isNotEmpty;
  }

  /// Gets the user's initials.
  String get initials => name.split(' ').map((n) => n[0]).join();

  /// Sets the user's email with validation.
  set userEmail(String? value) {
    if (value == null || value.contains('@')) {
      email = value;
    }
  }
}

/// Abstract service interface for user operations.
abstract class UserService {
  Future<User?> getUser(int id);
  Future<User> createUser(String name);
  Future<bool> deleteUser(int id);
}

/// Status enumeration for entities.
enum Status { active, inactive, pending }

/// Mixin for logging functionality.
mixin Loggable {
  /// Logs a message to console.
  void log(String message) {
    print('[LOG] $message');
  }

  /// Logs an error message.
  void logError(String error) {
    print('[ERROR] $error');
  }
}

/// Extension methods for String utilities.
extension StringUtils on String {
  /// Converts string to title case.
  String toTitleCase() {
    return split(' ').map((word) {
      if (word.isEmpty) return word;
      return word[0].toUpperCase() + word.substring(1).toLowerCase();
    }).join(' ');
  }

  /// Checks if string is a valid email.
  bool get isValidEmail => contains('@') && contains('.');
}

/// Default implementation of UserService with logging.
class DefaultUserService extends UserService with Loggable {
  final Map<int, User> _users = {};

  /// Retrieves a user by ID.
  @override
  Future<User?> getUser(int id) async {
    log('Getting user $id');
    return _users[id];
  }

  /// Creates a new user with the given name.
  @override
  Future<User> createUser(String name) async {
    final id = _users.length + 1;
    final user = User(id, name);
    _users[id] = user;
    log('Created user $name with id $id');
    return user;
  }

  /// Deletes a user by ID.
  @override
  Future<bool> deleteUser(int id) async {
    final removed = _users.remove(id) != null;
    if (removed) {
      log('Deleted user $id');
    } else {
      logError('User $id not found');
    }
    return removed;
  }
}

/// Top-level function for email validation.
bool validateEmail(String email) {
  return email.contains('@') && email.contains('.');
}

/// Async function to fetch user data.
Future<Map<String, dynamic>> fetchUserData(int userId) async {
  await Future.delayed(Duration(milliseconds: 100));
  return {'id': userId, 'name': 'User $userId'};
}
