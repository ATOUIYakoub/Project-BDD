
CREATE TABLE "account_user" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "username" varchar(120) NOT NULL, "email" varchar(254) NOT NULL UNIQUE, "password" varchar(255) NOT NULL, "is_admin" bool NOT NULL, "image_file" varchar(100) NULL, "is_authenticated" bool NOT NULL);

