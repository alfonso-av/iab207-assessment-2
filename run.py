from app import create_app, db

app = create_app()

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run()

print("\nRegistered routes:")
for rule in app.url_map.iter_rules():
    print(rule)
print()
