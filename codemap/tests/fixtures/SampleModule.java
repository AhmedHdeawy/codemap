package com.example.sample;

/**
 * Represents a user in the system.
 */
public class User {
    private int id;
    private String name;

    /**
     * Creates a new user.
     */
    public User(int id, String name) {
        this.id = id;
        this.name = name;
    }

    /**
     * Gets the user ID.
     */
    public int getId() {
        return id;
    }

    /**
     * Gets the user name.
     */
    public String getName() {
        return name;
    }
}

/**
 * Service interface for user operations.
 */
interface UserService {
    User getUser(int id);
    User createUser(String name);
}

/**
 * Status enumeration.
 */
enum Status {
    ACTIVE,
    INACTIVE,
    PENDING
}

/**
 * Default implementation of UserService.
 */
class DefaultUserService implements UserService {
    /**
     * Retrieves a user by ID.
     */
    @Override
    public User getUser(int id) {
        return new User(id, "Unknown");
    }

    /**
     * Creates a new user with the given name.
     */
    @Override
    public User createUser(String name) {
        return new User(1, name);
    }
}
