CREATE DATABASE app_warehouse;
CREATE USER 'load'@'localhost' IDENTIFIED BY 'password';
GRANT INSERT ON app_warehouse.* TO 'load'@'localhost';
GRANT SELECT ON app_warehouse.* TO 'load'@'localhost';
GRANT USAGE ON app_warehouse.* TO 'load'@'localhost';
FLUSH PRIVILEGES;
EXIT