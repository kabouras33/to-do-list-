import { createConnection, Connection } from 'typeorm';
import { User } from '../models/User';
import { Task } from '../models/Task';
import { RedisClient } from 'redis';
import { MongoClient } from 'mongodb';
import { config } from 'dotenv';

config();

interface DatabaseConfig {
  type: 'postgres' | 'mongodb';
  host: string;
  port: number;
  username: string;
  password: string;
  database: string;
}

const postgresConfig: DatabaseConfig = {
  type: 'postgres',
  host: process.env.POSTGRES_HOST || 'localhost',
  port: parseInt(process.env.POSTGRES_PORT || '5432', 10),
  username: process.env.POSTGRES_USER || 'user',
  password: process.env.POSTGRES_PASSWORD || 'password',
  database: process.env.POSTGRES_DB || 'todo_db',
};

const mongoConfig: DatabaseConfig = {
  type: 'mongodb',
  host: process.env.MONGO_HOST || 'localhost',
  port: parseInt(process.env.MONGO_PORT || '27017', 10),
  username: process.env.MONGO_USER || 'user',
  password: process.env.MONGO_PASSWORD || 'password',
  database: process.env.MONGO_DB || 'todo_db',
};

const redisConfig = {
  host: process.env.REDIS_HOST || 'localhost',
  port: parseInt(process.env.REDIS_PORT || '6379', 10),
};

let postgresConnection: Connection;
let mongoClient: MongoClient;
let redisClient: RedisClient;

export const connectPostgres = async (): Promise<Connection> => {
  if (!postgresConnection) {
    try {
      postgresConnection = await createConnection({
        type: postgresConfig.type,
        host: postgresConfig.host,
        port: postgresConfig.port,
        username: postgresConfig.username,
        password: postgresConfig.password,
        database: postgresConfig.database,
        entities: [User, Task],
        synchronize: true,
      });
      console.log('Connected to PostgreSQL');
    } catch (error) {
      console.error('Error connecting to PostgreSQL:', error);
      throw new Error('Database connection failed');
    }
  }
  return postgresConnection;
};

export const connectMongo = async (): Promise<MongoClient> => {
  if (!mongoClient) {
    try {
      mongoClient = new MongoClient(`mongodb://${mongoConfig.host}:${mongoConfig.port}`, {
        auth: {
          user: mongoConfig.username,
          password: mongoConfig.password,
        },
        useNewUrlParser: true,
        useUnifiedTopology: true,
      });
      await mongoClient.connect();
      console.log('Connected to MongoDB');
    } catch (error) {
      console.error('Error connecting to MongoDB:', error);
      throw new Error('Database connection failed');
    }
  }
  return mongoClient;
};

export const connectRedis = (): RedisClient => {
  if (!redisClient) {
    redisClient = new RedisClient({
      host: redisConfig.host,
      port: redisConfig.port,
    });
    redisClient.on('error', (error) => {
      console.error('Redis error:', error);
    });
    console.log('Connected to Redis');
  }
  return redisClient;
};

export const closeConnections = async () => {
  if (postgresConnection) {
    await postgresConnection.close();
    console.log('PostgreSQL connection closed');
  }
  if (mongoClient) {
    await mongoClient.close();
    console.log('MongoDB connection closed');
  }
  if (redisClient) {
    redisClient.quit();
    console.log('Redis connection closed');
  }
};