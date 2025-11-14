import { BackgroundTasks } from 'fastapi_utils.tasks';
import { Redis } from 'redis';
import { createClient } from 'redis';
import { Notification } from '../models/notification';
import { sendNotification } from '../services/notificationService';

const redisClient = createClient({
  url: process.env.REDIS_URL || 'redis://localhost:6379'
});

redisClient.on('error', (err) => {
  console.error('Redis Client Error', err);
});

redisClient.connect();

interface NotificationPayload {
  userId: string;
  message: string;
  type: string;
}

async function processNotificationJob(payload: NotificationPayload): Promise<void> {
  try {
    const notification = new Notification({
      userId: payload.userId,
      message: payload.message,
      type: payload.type,
      status: 'pending',
      createdAt: new Date()
    });

    await notification.save();

    const result = await sendNotification(payload.userId, payload.message, payload.type);

    notification.status = result.success ? 'sent' : 'failed';
    notification.sentAt = result.success ? new Date() : null;
    await notification.save();

    if (!result.success) {
      throw new Error('Failed to send notification');
    }
  } catch (error) {
    console.error('Error processing notification job:', error);
    throw error;
  }
}

const backgroundTasks = new BackgroundTasks();

backgroundTasks.add_task(processNotificationJob, {
  userId: '12345',
  message: 'Your task is due soon!',
  type: 'reminder'
});

export { processNotificationJob, backgroundTasks };