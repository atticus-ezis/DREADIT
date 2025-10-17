# User Authentication Walkthrough

## Intro

This is a detailed breakdown of how to design a secure and modern backend for User account creation with Django.

User account creation and management is a core requirement for almost every app. And considering your users may be entrusting you with sensitive personal information such as emails you owe it to them to manage their accounts as securly as possible. Knowing how to do this effectively and quickly is essential for backend devs.

The following is a documentation of my learning proccess, and a blue print to work around a lot of bugs which will arise when using these popular libraries. The goal is to recap my understanding and to hopefully save some of you a lot of precious time and effort.

If you are exploring Django Restframework and API development for JWT and Oauth2 this will be a good place to start.

## Background: How does authentication work?

The backend, or server, needs some way to recognize the user who is making the requests. This allows us to serve personalized content and keep user info secure.

There are different approaches available we'll touch on but know they all follow the same basic concept of Tokenization.

Tokenization is when the server validates the user by assigning them a unique token, which they can exchange for requests. Think of it like a valet ticket, or order number at a restuarant.

### There are two types of Tokenization: Stateful and Stateless.

**_Stateful_** the token is split in two parts. One is given to the User, the other is kept in the Database. To validate the User's token a database lookup needs to be preformed.
**_Stateless_** the token remains whole. This means it isn't stored in the database and no lookups need to occur. Instead it is automatically validated once presented.

**_A Useful Analogy_**
Think of Stateful Tokens like a hotel front desk. You need to provide a name and ID for an existing booking before you get access to your room.
Stateless on the other hand is the room card itself. The authentication is self-contained in that card. Anyone who holds it has access, no further verification is required.

### Which is best?

While Stateful transactions sound more secure there are other considerations which need to be taken into account.

Stateless is faster: No backend lookups or database storage behind the scenes means it scales well with high-traffic.

Stateless is more API friendly: In larger, more complex apps that often call on multiple containers or servers (Redis, Docker, AWS load balancer, etc..) relying on each to synchronize and validate token records creates headaches.

Beacuse Stateless tokens are self-contained they can be used across every server with no extra configuration. This is more reliable and effecient.

So Stateless wins for conveiance and scalability. What about security?

The advantage that Stateful tokens have is that they're directly in your control. You have half the token in your database which you can revoke at anytime. But because Stateless tokens are pre-validated you can't easily deny access to anyone who has them.

Because of this it is the modern standard.

### The Goal

- **Create APIs that frontend can use for all things related to the user's account**

## Overview

First I installed and configured allauth and dj rest auth.
These libraries provide default User creation and management. However in order for them to work properly we need to fine tune them.

What are Web Tokens?

- a secret handshake bewteen the client and the server that lets the server know exactly who is making the request.
- this ensures the right information reaches the right people.
- important for security and for serving personalized settings and information

Which web token is best?

Typically Django uses a one t

Because I'm working with a front end I want to use JWT to authenticate users. Advantages of this is that these tokens are stateless, can automatically regenerate and are more secure and convient to use.

# In settings.py

SESSION_COOKIE_SAMESITE = 'Lax' # Prevents CSRF in most cases
CSRF_COOKIE_SAMESITE = 'Lax'

# For production with HTTPS:

if PRODUCTION:
SESSION_COOKIE_SECURE = True  
 CSRF_COOKIE_SECURE = True  
 SESSION_COOKIE_SAMESITE = 'Strict'

## Configure REST_Framework

- install drf + simplejwt
- set jwt auth and cookies
- under REST_FRAMEWORK = {}

## Configure JWT

- Install restframework-simplejwt
- SIMPLE_JWT = {} in settings.py
- set "ROTATE_REFRESH_TOKENS": True,
- "BLACKLIST_AFTER_ROTATION": True,
- this is more secure and best practice.

## Configure AllAuth

- AllAuth handles the email requests under the hood of dj rest auth

- Here you can customize things like signup info and manage the behaviour of email verification messages.

- ACCOUNT_EMAIL_VERIFICATION 'optional'
- ACCOUNT_ADAPTER 'used to send custom email confirmation link'

## Configure Dj-rest-auth

- specify that we're using JWT not the default token
- specify the user detail serializer

## Configure Email

- use mailpit in development and match EMAIL_PORT

## Configure CORS and Site ID for frontend
