import { Session } from 'sqlalchemy';
import { HTTPException, status } from 'fastapi';
import { TaskService } from './task_service';
import { Task, TaskCreate, TaskUpdate } from './models';
import { jest } from '@jest/globals';

describe('TaskService', () => {
  let mockDb: jest.Mocked<Session>;
  let taskService: TaskService;

  beforeEach(() => {
    mockDb = {
      query: jest.fn(),
      add: jest.fn(),
      commit: jest.fn(),
      rollback: jest.fn(),
      refresh: jest.fn(),
      delete: jest.fn(),
    } as unknown as jest.Mocked<Session>;

    taskService = new TaskService(mockDb);
  });

  describe('get_tasks', () => {
    it('should return tasks for a valid user_id', async () => {
      const mockTasks = [{ id: 1, user_id: 1 }, { id: 2, user_id: 1 }];
      mockDb.query.mockReturnValue({
        filter: jest.fn().mockReturnValue({
          all: jest.fn().mockReturnValue(mockTasks),
        }),
      });

      const result = await taskService.get_tasks(1);

      expect(result).toEqual(mockTasks);
      expect(mockDb.query).toHaveBeenCalledWith(Task);
    });

    it('should throw HTTP 404 if no tasks found', async () => {
      mockDb.query.mockReturnValue({
        filter: jest.fn().mockReturnValue({
          all: jest.fn().mockReturnValue([]),
        }),
      });

      await expect(taskService.get_tasks(1)).rejects.toThrow(
        new HTTPException({
          status_code: status.HTTP_404_NOT_FOUND,
          detail: 'No tasks found',
        })
      );
    });

    it('should throw HTTP 500 on database error', async () => {
      mockDb.query.mockImplementation(() => {
        throw new Error('DB error');
      });

      await expect(taskService.get_tasks(1)).rejects.toThrow(
        new HTTPException({
          status_code: status.HTTP_500_INTERNAL_SERVER_ERROR,
          detail: 'DB error',
        })
      );
    });
  });

  describe('create_task', () => {
    it('should create a new task successfully', async () => {
      const taskData = { title: 'New Task', description: 'Task description' };
      const mockTask = { id: 1, ...taskData, user_id: 1, created_at: new Date() };
      mockDb.add.mockImplementation(() => {});
      mockDb.commit.mockImplementation(() => {});
      mockDb.refresh.mockImplementation((task) => Object.assign(task, mockTask));

      const result = await taskService.create_task(taskData as TaskCreate, 1);

      expect(result).toEqual(mockTask);
      expect(mockDb.add).toHaveBeenCalled();
      expect(mockDb.commit).toHaveBeenCalled();
      expect(mockDb.refresh).toHaveBeenCalled();
    });

    it('should rollback and throw HTTP 500 on error', async () => {
      mockDb.add.mockImplementation(() => {
        throw new Error('DB error');
      });

      await expect(taskService.create_task({} as TaskCreate, 1)).rejects.toThrow(
        new HTTPException({
          status_code: status.HTTP_500_INTERNAL_SERVER_ERROR,
          detail: 'DB error',
        })
      );

      expect(mockDb.rollback).toHaveBeenCalled();
    });
  });

  describe('update_task', () => {
    it('should update an existing task successfully', async () => {
      const taskData = { title: 'Updated Task' };
      const mockTask = { id: 1, user_id: 1, title: 'Old Task' };
      mockDb.query.mockReturnValue({
        filter: jest.fn().mockReturnValue({
          first: jest.fn().mockReturnValue(mockTask),
        }),
      });
      mockDb.commit.mockImplementation(() => {});
      mockDb.refresh.mockImplementation((task) => Object.assign(task, taskData));

      const result = await taskService.update_task(1, taskData as TaskUpdate, 1);

      expect(result.title).toEqual('Updated Task');
      expect(mockDb.commit).toHaveBeenCalled();
      expect(mockDb.refresh).toHaveBeenCalled();
    });

    it('should throw HTTP 404 if task not found', async () => {
      mockDb.query.mockReturnValue({
        filter: jest.fn().mockReturnValue({
          first: jest.fn().mockReturnValue(null),
        }),
      });

      await expect(taskService.update_task(1, {} as TaskUpdate, 1)).rejects.toThrow(
        new HTTPException({
          status_code: status.HTTP_404_NOT_FOUND,
          detail: 'Task not found',
        })
      );
    });

    it('should rollback and throw HTTP 500 on error', async () => {
      mockDb.query.mockImplementation(() => {
        throw new Error('DB error');
      });

      await expect(taskService.update_task(1, {} as TaskUpdate, 1)).rejects.toThrow(
        new HTTPException({
          status_code: status.HTTP_500_INTERNAL_SERVER_ERROR,
          detail: 'DB error',
        })
      );

      expect(mockDb.rollback).toHaveBeenCalled();
    });
  });

  describe('delete_task', () => {
    it('should delete an existing task successfully', async () => {
      const mockTask = { id: 1, user_id: 1 };
      mockDb.query.mockReturnValue({
        filter: jest.fn().mockReturnValue({
          first: jest.fn().mockReturnValue(mockTask),
        }),
      });
      mockDb.commit.mockImplementation(() => {});

      await taskService.delete_task(1, 1);

      expect(mockDb.delete).toHaveBeenCalledWith(mockTask);
      expect(mockDb.commit).toHaveBeenCalled();
    });

    it('should throw HTTP 404 if task not found', async () => {
      mockDb.query.mockReturnValue({
        filter: jest.fn().mockReturnValue({
          first: jest.fn().mockReturnValue(null),
        }),
      });

      await expect(taskService.delete_task(1, 1)).rejects.toThrow(
        new HTTPException({
          status_code: status.HTTP_404_NOT_FOUND,
          detail: 'Task not found',
        })
      );
    });

    it('should rollback and throw HTTP 500 on error', async () => {
      mockDb.query.mockImplementation(() => {
        throw new Error('DB error');
      });

      await expect(taskService.delete_task(1, 1)).rejects.toThrow(
        new HTTPException({
          status_code: status.HTTP_500_INTERNAL_SERVER_ERROR,
          detail: 'DB error',
        })
      );

      expect(mockDb.rollback).toHaveBeenCalled();
    });
  });

  describe('get_task_by_id', () => {
    it('should return a task for a valid task_id and user_id', async () => {
      const mockTask = { id: 1, user_id: 1 };
      mockDb.query.mockReturnValue({
        filter: jest.fn().mockReturnValue({
          first: jest.fn().mockReturnValue(mockTask),
        }),
      });

      const result = await taskService.get_task_by_id(1, 1);

      expect(result).toEqual(mockTask);
    });

    it('should throw HTTP 404 if task not found', async () => {
      mockDb.query.mockReturnValue({
        filter: jest.fn().mockReturnValue({
          first: jest.fn().mockReturnValue(null),
        }),
      });

      await expect(taskService.get_task_by_id(1, 1)).rejects.toThrow(
        new HTTPException({
          status_code: status.HTTP_404_NOT_FOUND,
          detail: 'Task not found',
        })
      );
    });

    it('should throw HTTP 500 on database error', async () => {
      mockDb.query.mockImplementation(() => {
        throw new Error('DB error');
      });

      await expect(taskService.get_task_by_id(1, 1)).rejects.toThrow(
        new HTTPException({
          status_code: status.HTTP_500_INTERNAL_SERVER_ERROR,
          detail: 'DB error',
        })
      );
    });
  });
});