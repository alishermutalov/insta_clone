# Insta Clone API

An Instagram-like social media platform built with Django and Django REST Framework. This project allows users to create posts, like posts, comment on posts, like comments, and manage user accounts.

## Features

- User authentication and management (Signup, Login, Logout)
- Email verification
- Post creation, update, and deletion
- Commenting on posts
- Liking posts and comments
- Swagger and Redoc API documentation

## Project Structure

The project is organized into two main apps:
1. **Users**: Manages user authentication and profiles.
2. **Posts**: Handles the creation, update, and management of posts, comments, and likes.

## API Endpoints

### Users
- `POST /users/signup/` - Register a new user
- `POST /users/login/` - Login an existing user
- `POST /users/login/refresh/` - Refresh login token
- `POST /users/logout/` - Logout the user
- `POST /users/verify/` - Verify email
- `POST /users/verify/resend/` - Resend verification code
- `PUT /users/update-user/` - Update user information
- `POST /users/update-user-photo/` - Set or update user photo
- `POST /users/forgot-password/` - Initiate password reset process
- `POST /users/reset-password/` - Reset user password

### Posts
- `GET /post/list/` - List all posts
- `POST /post/create/` - Create a new post
- `GET /post/<uuid:pk>/` - Retrieve, update, or delete a post by its UUID
- `GET /post/<uuid:pk>/comments/` - List all comments on a post
- `POST /post/<uuid:pk>/comments/create/` - Create a comment on a post
- `DELETE /post/comments/delete/<uuid:pk>/` - Delete a comment
- `GET /post/<uuid:pk>/likes/` - List all likes on a post
- `POST /post/<uuid:pk>/likes/create/` - Like a post
- `DELETE /post/<uuid:pk>/likes/delete/` - Remove like from a post
- `GET /post/comments/<uuid:pk>/` - Retrieve details of a specific comment
- `GET /post/comments/<uuid:pk>/likes/` - List all likes on a comment
- `POST /post/comments/<uuid:pk>/likes/create/` - Like a comment
- `DELETE /post/comments/<uuid:pk>/likes/delete/` - Remove like from a comment

## API Documentation

- Swagger UI: `/swagger/`
- Redoc: `/redoc/`

The API documentation is generated using `drf-yasg` and is accessible through the above URLs.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/alishermutalov/insta_clone.git
   cd insta_clone
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```bash
   python manage.py migrate
   ```

5. Run the development server:
   ```bash
   python manage.py runserver
   ```

6. Access the API at `http://127.0.0.1:8000/`.

## Settings

- **STATIC_URL** and **MEDIA_URL** are set in `settings.py` to serve static and media files. Be sure to configure these properly in a production environment.
  
- To enable Swagger and Redoc for API documentation, `drf-yasg` is used. Permissions for API documentation access are configured with `permissions.AllowAny`.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or issues, please contact [amutalov001@gmail.com](mailto:amutalov001@gmail.com).
```

