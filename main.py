import app.database.models

from app.database.database import Base, engine


def main():
    Base.metadata.create_all(bind=engine)
    print("Database created successfully!")


if __name__ == "__main__":
    main()