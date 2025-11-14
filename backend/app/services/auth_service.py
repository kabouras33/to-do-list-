import { jest } from '@jest/globals';
import { HTTPException } from 'fastapi';
import { Session } from 'sqlalchemy';
import { JWTError, jwt } from 'jose';
import { CryptContext } from 'passlib';
import { datetime, timedelta } from 'datetime';
import { models, schemas } from './models';
import { get_db } from './database';
import { settings } from './config';
import {
  verify_password,
  get_password_hash,
  authenticate_user,
  create_access_token,
  get_current_user,
  get_current_active_user
} from './auth_service';

jest.mock('./database');
jest.mock('jose');
jest.mock('passlib');
jest.mock('./config');

describe('AuthService', () => {
  const mockDb = jest.fn() as unknown as Session;
  const mockUser = { username: 'testuser', hashed_password: 'hashedpassword', is_active: true };
  const mockToken = 'mocktoken';
  const mockDecodedToken = { sub: 'testuser' };

  beforeEach(() => {
    jest.clearAllMocks();
    get_db.mockReturnValue(mockDb);
    settings.SECRET_KEY = 'secretkey';
  });

  describe('verify_password', () => {
    it('should return true when password matches hash', () => {
      // Arrange
      const plainPassword = 'password';
      const hashedPassword = 'hashedpassword';
      CryptContext.prototype.verify = jest.fn().mockReturnValue(true);

      // Act
      const result = verify_password(plainPassword, hashedPassword);

      // Assert
      expect(result).toBe(true);
    });

    it('should return false when password does not match hash', () => {
      // Arrange
      const plainPassword = 'password';
      const hashedPassword = 'wronghash';
      CryptContext.prototype.verify = jest.fn().mockReturnValue(false);

      // Act
      const result = verify_password(plainPassword, hashedPassword);

      // Assert
      expect(result).toBe(false);
    });
  });

  describe('get_password_hash', () => {
    it('should return a hashed password', () => {
      // Arrange
      const password = 'password';
      const hashedPassword = 'hashedpassword';
      CryptContext.prototype.hash = jest.fn().mockReturnValue(hashedPassword);

      // Act
      const result = get_password_hash(password);

      // Assert
      expect(result).toBe(hashedPassword);
    });
  });

  describe('authenticate_user', () => {
    it('should return user when credentials are valid', () => {
      // Arrange
      mockDb.query = jest.fn().mockReturnValue({
        filter: jest.fn().mockReturnValue({
          first: jest.fn().mockReturnValue(mockUser)
        })
      });
      CryptContext.prototype.verify = jest.fn().mockReturnValue(true);

      // Act
      const result = authenticate_user(mockDb, 'testuser', 'password');

      // Assert
      expect(result).toEqual(mockUser);
    });

    it('should return null when user does not exist', () => {
      // Arrange
      mockDb.query = jest.fn().mockReturnValue({
        filter: jest.fn().mockReturnValue({
          first: jest.fn().mockReturnValue(null)
        })
      });

      // Act
      const result = authenticate_user(mockDb, 'nonexistent', 'password');

      // Assert
      expect(result).toBeNull();
    });

    it('should return null when password is incorrect', () => {
      // Arrange
      mockDb.query = jest.fn().mockReturnValue({
        filter: jest.fn().mockReturnValue({
          first: jest.fn().mockReturnValue(mockUser)
        })
      });
      CryptContext.prototype.verify = jest.fn().mockReturnValue(false);

      // Act
      const result = authenticate_user(mockDb, 'testuser', 'wrongpassword');

      // Assert
      expect(result).toBeNull();
    });
  });

  describe('create_access_token', () => {
    it('should return a JWT token', () => {
      // Arrange
      const data = { sub: 'testuser' };
      const expiresDelta = timedelta(minutes=60);
      const expectedToken = 'encodedtoken';
      jwt.encode = jest.fn().mockReturnValue(expectedToken);

      // Act
      const result = create_access_token(data, expiresDelta);

      // Assert
      expect(result).toBe(expectedToken);
    });
  });

  describe('get_current_user', () => {
    it('should return user when token is valid', async () => {
      // Arrange
      jwt.decode = jest.fn().mockReturnValue(mockDecodedToken);
      mockDb.query = jest.fn().mockReturnValue({
        filter: jest.fn().mockReturnValue({
          first: jest.fn().mockReturnValue(mockUser)
        })
      });

      // Act
      const result = await get_current_user(mockDb, mockToken);

      // Assert
      expect(result).toEqual(mockUser);
    });

    it('should throw HTTPException when token is invalid', async () => {
      // Arrange
      jwt.decode = jest.fn().mockImplementation(() => { throw new JWTError(); });

      // Act & Assert
      await expect(get_current_user(mockDb, mockToken)).rejects.toThrow(HTTPException);
    });

    it('should throw HTTPException when user is not found', async () => {
      // Arrange
      jwt.decode = jest.fn().mockReturnValue(mockDecodedToken);
      mockDb.query = jest.fn().mockReturnValue({
        filter: jest.fn().mockReturnValue({
          first: jest.fn().mockReturnValue(null)
        })
      });

      // Act & Assert
      await expect(get_current_user(mockDb, mockToken)).rejects.toThrow(HTTPException);
    });
  });

  describe('get_current_active_user', () => {
    it('should return active user', async () => {
      // Arrange
      const activeUser = { ...mockUser, is_active: true };

      // Act
      const result = await get_current_active_user(activeUser);

      // Assert
      expect(result).toEqual(activeUser);
    });

    it('should throw HTTPException when user is inactive', async () => {
      // Arrange
      const inactiveUser = { ...mockUser, is_active: false };

      // Act & Assert
      await expect(get_current_active_user(inactiveUser)).rejects.toThrow(HTTPException);
    });
  });
});