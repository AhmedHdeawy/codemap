<?php

/**
 * Sample PHP module for testing the PHP parser.
 * Demonstrates PHP 8+ features including classes, interfaces, traits, enums, and attributes.
 */

namespace Codemap\Tests;

use DateTime;
use Exception;

/**
 * UserStatus represents the possible states of a user account.
 */
enum UserStatus: string
{
    case Active = 'active';
    case Inactive = 'inactive';
    case Pending = 'pending';
}

/**
 * Represents a basic color with RGB values.
 */
enum Color
{
    case Red;
    case Green;
    case Blue;
}

/**
 * Interface for repositories that handle data persistence.
 */
interface RepositoryInterface
{
    /**
     * Find an entity by its ID.
     */
    public function find(int $id): ?object;

    /**
     * Save an entity to the repository.
     */
    public function save(object $entity): void;

    /**
     * Delete an entity from the repository.
     */
    public function delete(int $id): bool;
}

/**
 * Trait providing timestamp functionality.
 */
trait Timestampable
{
    private ?DateTime $createdAt = null;
    private ?DateTime $updatedAt = null;

    /**
     * Get the creation timestamp.
     */
    public function getCreatedAt(): ?DateTime
    {
        return $this->createdAt;
    }

    /**
     * Set the creation timestamp.
     */
    public function setCreatedAt(DateTime $createdAt): self
    {
        $this->createdAt = $createdAt;
        return $this;
    }

    /**
     * Update the modification timestamp.
     */
    public function touch(): void
    {
        $this->updatedAt = new DateTime();
    }
}

/**
 * User entity representing a system user.
 */
#[Entity(table: 'users')]
class User
{
    use Timestampable;

    /**
     * Create a new user instance.
     */
    public function __construct(
        private readonly int $id,
        private string $name,
        private string $email,
        private UserStatus $status = UserStatus::Pending,
    ) {
        $this->createdAt = new DateTime();
    }

    /**
     * Get the user's ID.
     */
    public function getId(): int
    {
        return $this->id;
    }

    /**
     * Get the user's name.
     */
    public function getName(): string
    {
        return $this->name;
    }

    /**
     * Set the user's name.
     */
    public function setName(string $name): self
    {
        $this->name = $name;
        return $this;
    }

    /**
     * Get the user's email address.
     */
    public function getEmail(): string
    {
        return $this->email;
    }

    /**
     * Check if the user is active.
     */
    public function isActive(): bool
    {
        return $this->status === UserStatus::Active;
    }

    /**
     * Activate the user account.
     */
    #[RequiresPermission('admin')]
    public function activate(): void
    {
        $this->status = UserStatus::Active;
        $this->touch();
    }
}

/**
 * Abstract base class for services.
 */
abstract class AbstractService
{
    /**
     * Initialize the service.
     */
    abstract public function initialize(): void;

    /**
     * Get the service name.
     */
    public function getServiceName(): string
    {
        return static::class;
    }
}

/**
 * User service for managing user operations.
 */
class UserService extends AbstractService implements RepositoryInterface
{
    private array $users = [];

    /**
     * Initialize the user service.
     */
    public function initialize(): void
    {
        // Load initial data
    }

    /**
     * Find a user by ID.
     */
    public function find(int $id): ?User
    {
        return $this->users[$id] ?? null;
    }

    /**
     * Save a user entity.
     */
    public function save(object $entity): void
    {
        if ($entity instanceof User) {
            $this->users[$entity->getId()] = $entity;
        }
    }

    /**
     * Delete a user by ID.
     */
    public function delete(int $id): bool
    {
        if (isset($this->users[$id])) {
            unset($this->users[$id]);
            return true;
        }
        return false;
    }

    /**
     * Get all active users using an arrow function.
     */
    public function getActiveUsers(): array
    {
        return array_filter(
            $this->users,
            fn(User $user): bool => $user->isActive()
        );
    }

    /**
     * Process users with a callback.
     */
    public function processUsers(callable $callback): void
    {
        array_walk($this->users, $callback);
    }
}

/**
 * Greet a user by name.
 */
function greet(string $name): string
{
    return "Hello, {$name}!";
}

/**
 * Calculate the sum of numbers.
 */
function sum(int ...$numbers): int
{
    return array_sum($numbers);
}

/**
 * Create a multiplier function.
 */
function createMultiplier(int $factor): callable
{
    return fn(int $value): int => $value * $factor;
}
