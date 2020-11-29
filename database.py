import functools
import sqlite3


def db_connection(func):
    """Must to use this in all public methods of PackingDB"""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        self.connection = sqlite3.connect(f"{self.db_path}")
        self.cursor = self.connection.cursor()
        self.cursor.execute("""PRAGMA foreign_keys = ON""")
        func_value = func(self, *args, **kwargs)
        self.cursor.close()
        return func_value

    return wrapper


class ProjectsDb:
    def __init__(self, path: str):
        self.db_path = path

    @db_connection
    def create_table(self):
        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS projects
        (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            first_date DATE NOT NULL,
            last_date DATE NOT NULL,
            color VARCHAR(6),
            status int
        )""")
        self.connection.commit()

    @db_connection
    def add_project(self, project_name, first_date, last_date, color="B9C4C9", status=0):
        self.cursor.execute(f"""INSERT INTO projects (project_name, first_date, last_date, color, status) 
                                VALUES (:project_name, '{first_date}', '{last_date}', '{color}', '{status}') """,
                            {"project_name": project_name})
        self.cursor.execute(f"""SELECT LAST_INSERT_ROWID() from projects""")
        last_id = self.cursor.fetchone()[0]
        self.connection.commit()
        return last_id

    @db_connection
    def get_projects(self):
        self.cursor.execute(f"""SELECT id, project_name, first_date, last_date, color, status from projects""")
        content = []
        for row in self.cursor:
            content.append(row)
        return content

    @db_connection
    def drop_projects(self):
        self.cursor.execute(f"""DROP TABLE IF EXISTS projects""")
        self.connection.commit()

    @db_connection
    def update_color(self, project_id, new_color):
        self.cursor.execute(f"""UPDATE projects SET color = "{new_color}" WHERE id = {project_id}""")
        self.connection.commit()

    @db_connection
    def update_status(self, project_id, new_status):
        self.cursor.execute(f"""UPDATE projects SET status = "{new_status}" WHERE id = {project_id}""")
        self.connection.commit()

    @db_connection
    def update_date(self, project_id, new_first_date, new_last_date):
        self.cursor.execute(f"""UPDATE projects SET first_date = "{new_first_date}",
                                last_date = "{new_last_date}" WHERE id = {project_id}""")
        self.connection.commit()

    @db_connection
    def update_name(self, project_id, new_name):
        self.cursor.execute(f"""UPDATE projects SET project_name = :new_name WHERE id = {project_id}""",
                            {"new_name": new_name})
        self.connection.commit()

    @db_connection
    def delete_project(self, project_id):
        self.cursor.execute(f"""DELETE FROM projects WHERE id = {project_id}""")
        self.connection.commit()


if __name__ != "__main__":
    db = ProjectsDb("projects.db")
    db.create_table()

if __name__ == "__main__":
    db = ProjectsDb("projects.db")
    db.drop_projects()
    db.create_table()
    db.add_project('first project', "2020-11-23", "2020-12-27")
    db.add_project('second project', "2020-10-25", "2020-10-27")
    db.add_project('third project', "2020-10-10", "2020-10-30")
    db.add_project('third project', "2020-10-10", "2020-10-30")
    db.add_project('third project', "2020-10-15", "2020-11-24")
    db.add_project('third project', "2020-10-18", "2020-10-25")
    db.add_project('third project', "2020-10-10", "2020-10-30")

    projects = db.get_projects()
    print(projects)