// Package sample provides sample Go code for testing.
package sample

import "fmt"

// User represents a user in the system.
type User struct {
	ID   int
	Name string
}

// UserService handles user operations.
type UserService interface {
	GetUser(id int) (*User, error)
	CreateUser(name string) (*User, error)
}

// DefaultService is the default implementation.
type DefaultService struct {
	users map[int]*User
}

// GetUser retrieves a user by ID.
func (s *DefaultService) GetUser(id int) (*User, error) {
	if user, ok := s.users[id]; ok {
		return user, nil
	}
	return nil, fmt.Errorf("user not found")
}

// CreateUser creates a new user.
func (s *DefaultService) CreateUser(name string) (*User, error) {
	user := &User{ID: len(s.users) + 1, Name: name}
	s.users[user.ID] = user
	return user, nil
}

// Helper function for greeting.
func Greet(name string) string {
	return fmt.Sprintf("Hello, %s!", name)
}

// Process handles async-like operations.
func Process(data []byte) ([]byte, error) {
	return data, nil
}
