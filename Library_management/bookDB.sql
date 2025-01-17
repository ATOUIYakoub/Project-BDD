BEGIN;
--
-- Create model Book
--
CREATE TABLE "book_book" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(80) NOT NULL, "description" varchar(500) NOT NULL, "author" varchar(150) NOT NULL, "quantity" integer NOT NULL, "thumbnail" varchar(100) NULL);
--
-- Create model Category
--
CREATE TABLE "book_category" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(80) NOT NULL UNIQUE);
--
-- Create model BookInstance
--
CREATE TABLE "book_bookinstance" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "due_back" datetime NOT NULL, "loan_status" bool NOT NULL, "book_id" bigint NOT NULL REFERENCES "book_book" ("id") DEFERRABLE INITIALLY DEFERRED, "borrower_id" bigint NOT NULL REFERENCES "account_user" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Add field category to book
--
CREATE TABLE "new__book_book" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(80) NOT NULL, "description" varchar(500) NOT NULL, "author" varchar(150) NOT NULL, "quantity" integer NOT NULL, "thumbnail" varchar(100) NULL, "category_id" bigint NOT NULL REFERENCES "book_category" ("id") DEFERRABLE INITIALLY DEFERRED);
INSERT INTO "new__book_book" ("id", "title", "description", "author", "quantity", "thumbnail", "category_id") SELECT "id", "title", "description", "author", "quantity", "thumbnail", NULL FROM "book_book";
DROP TABLE "book_book";
ALTER TABLE "new__book_book" RENAME TO "book_book";
CREATE INDEX "book_bookinstance_book_id_4309ee0e" ON "book_bookinstance" ("book_id");
CREATE INDEX "book_bookinstance_borrower_id_1e818eba" ON "book_bookinstance" ("borrower_id");
CREATE INDEX "book_book_category_id_616006cd" ON "book_book" ("category_id");
COMMIT;
