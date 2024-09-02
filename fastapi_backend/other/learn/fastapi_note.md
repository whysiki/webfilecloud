## FastAPI Dependency Injection

FastAPI's Depends function is a powerful tool that allows you to express dependencies between different parts of your application. It can be used for a variety of purposes, such as:

Dependency Injection: You can use Depends to inject instances of classes or functions into your route handlers. This can be useful for things like database sessions or configuration objects.

Request Validation: You can use Depends to validate incoming requests and ensure that they meet certain criteria before they reach your route handlers.

Authentication and Authorization: You can use Depends to implement authentication and authorization in your application. You can create a dependency that checks if the current user is authenticated and has the necessary permissions to perform a certain action.

```python
# Depend db session
def get_db():
    db = models.SessionLocal()
    try:
        yield db
    finally:
        db.close()
```
if I use depend to inject dbsession, than the session will automatically open and close?

Yes, if you use FastAPI's Depends to inject the db session, it will automatically handle the opening and closing of the session for you. This is because the get_db function is a generator function that uses the yield keyword.

Here's how it works:

When a request comes in, FastAPI will call the get_db function. This function creates a new session with db = models.SessionLocal().
The get_db function then yields the db session, effectively pausing the function and sending the db session back to FastAPI.
FastAPI injects the db session into your route function (in this case, register_user). You can then use this session to interact with the database.
Once your route function finishes executing, FastAPI will resume the get_db function from where it left off (right after the yield statement). The finally block will then execute, closing the db session.


## 422 Unprocessable Entity

The 422 Unprocessable Entity error typically indicates that the data sent to the FastAPI endpoint does not conform to the expected schema or data types. In this case, it seems the FastAPI endpoint expects the user_in object as a JSON body, but a GET request with query parameters is being used.

To fix this, you have two options:

Modify the FastAPI endpoint to accept query parameters.
Change the request to a POST request and send the user_in object as JSON.



![alt text](images/fastapi_note/image.png)