#!/usr/bin/env python3

import sshtunnel
import mariadb


class MariaDBSSHConnector:
    def __init__(self, ssh_host, ssh_user, db_user, db_password,
                 ssh_password=None, ssh_private_key=None,
                 db_host="localhost", db_port=3306, db_name=None):
        self.ssh_host = ssh_host
        self.ssh_user = ssh_user
        self.ssh_password = ssh_password
        self.ssh_private_key = ssh_private_key
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name
        self.server = None
        self.conn = None

    def __enter__(self):
        self.open_tunnel()
        self.connect_to_db()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_db_connection()
        self.close_tunnel()

    def open_tunnel(self):
        try:
            if self.ssh_private_key:
                self.server = sshtunnel.SSHTunnelForwarder(
                    (self.ssh_host, 22),
                    ssh_username=self.ssh_user,
                    ssh_private_key=self.ssh_private_key,
                    remote_bind_address=(self.db_host, self.db_port)
                )
            else:
                self.server = sshtunnel.SSHTunnelForwarder(
                    (self.ssh_host, 22),
                    ssh_username=self.ssh_user,
                    ssh_password=self.ssh_password,
                    remote_bind_address=(self.db_host, self.db_port)
                )
            self.server.start()
        except Exception as e:
            raise Exception(f"Erreur lors de l'ouverture du tunnel SSH : {e}")

    def connect_to_db(self):
        try:
            self.conn = mariadb.connect(
                user=self.db_user,
                password=self.db_password,
                host="127.0.0.1",
                port=self.server.local_bind_port,
                database=self.db_name
            )
        except mariadb.Error as e:
            raise Exception(f"Erreur lors de la connexion à MariaDB : {e}")

    def close_db_connection(self):
        if self.conn:
            self.conn.close()

    def close_tunnel(self):
        if self.server:
            self.server.stop()

    def execute_query(self, query):

        if self.conn:
            try:
                cur = self.conn.cursor()
                cur.execute(query)
                return cur.fetchall()
            except mariadb.Error as e:
                raise Exception(f"Erreur lors de l'exécution de la requête : {e}")
        else:
            raise Exception("Not connected to the database")

    def insert_data(self, table, data):
        if self.conn:
            try:
                columns = ', '.join(data.keys())
                values = ', '.join([f"'{value}'" for value in data.values()])
                query = f"INSERT INTO {table} ({columns}) VALUES ({values})"
                cur = self.conn.cursor()
                cur.execute(query)
                self.conn.commit()  # Valider la transaction
            except mariadb.Error as e:
                raise Exception(f"Erreur lors de l'insertion des données : {e}")
        else:
            raise Exception("Not connected to the database")

    def update_data(self, table, data, where_clause):
        if self.conn:
            try:
                set_clause = ', '.join([f"{column} = '{value}'" for column, value in data.items()])
                query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
                cur = self.conn.cursor()
                cur.execute(query)
                self.conn.commit()
            except mariadb.Error as e:
                raise Exception(f"Erreur lors de la mise à jour des données : {e}")
        else:
            raise Exception("Not connected to the database")

    def delete_data(self, table, where_clause):
        if self.conn:
            try:
                query = f"DELETE FROM {table} WHERE {where_clause}"
                cur = self.conn.cursor()
                cur.execute(query)
                self.conn.commit()
            except mariadb.Error as e:
                raise Exception(f"Erreur lors de la suppression des données : {e}")
        else:
            raise Exception("Not connected to the database")


if __name__ == "__main__":
    print()
