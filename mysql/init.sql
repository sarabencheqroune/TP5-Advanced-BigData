CREATE TABLE IF NOT EXISTS cars (
  Car VARCHAR(255) NOT NULL PRIMARY KEY,
  MPG DOUBLE,
  Cylinders DOUBLE,
  Displacement DOUBLE,
  Horsepower INT,
  Weight INT,
  Acceleration DOUBLE,
  Model INT,
  Origin VARCHAR(10)
);