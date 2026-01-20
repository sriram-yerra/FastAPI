'''
What is Password Hashing?
    1. Password hashing is a one-way process that converts a plain-text password into an irreversible scrambled string.
    2. The original password cannot be recovered from the hash.
    3. Only the hashed password is stored in the database, never the raw password.
    4. This protects user credentials even if the database is leaked.
    5. During login, the entered password is hashed again and compared with the stored hash.
    6. Common Python libraries for hashing are passlib and bcrypt.
    7. Password hashing is a core requirement for secure authentication systems.
'''