using System;
using System.Threading.Tasks;

namespace Sample
{
    /// <summary>
    /// Represents a user in the system.
    /// </summary>
    public class User
    {
        public int Id { get; set; }
        public string Name { get; set; }

        /// <summary>
        /// Creates a new user.
        /// </summary>
        public User(int id, string name)
        {
            Id = id;
            Name = name;
        }

        /// <summary>
        /// Gets the display name.
        /// </summary>
        public string GetDisplayName()
        {
            return $"User: {Name}";
        }
    }

    /// <summary>
    /// Service interface for user operations.
    /// </summary>
    public interface IUserService
    {
        User GetUser(int id);
        Task<User> CreateUserAsync(string name);
    }

    /// <summary>
    /// User status enumeration.
    /// </summary>
    public enum UserStatus
    {
        Active,
        Inactive,
        Pending
    }

    /// <summary>
    /// Configuration structure.
    /// </summary>
    public struct Config
    {
        public string ApiUrl;
        public int Timeout;
    }

    /// <summary>
    /// Default implementation of IUserService.
    /// </summary>
    public class DefaultUserService : IUserService
    {
        /// <summary>
        /// Retrieves a user by ID.
        /// </summary>
        public User GetUser(int id)
        {
            return new User(id, "Unknown");
        }

        /// <summary>
        /// Creates a new user asynchronously.
        /// </summary>
        public async Task<User> CreateUserAsync(string name)
        {
            await Task.Delay(100);
            return new User(1, name);
        }
    }
}
