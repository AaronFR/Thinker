 /*
   * For queueing actions in cases where we need to wait for the frontend to update before processing an action
   */
class UpdateQueue {
  constructor() {
    this.queue = [];
    this.isProcessing = false;
  }

  enqueue(updateData) {
    this.queue.push(updateData)
    this.processQueue()
  }

  async processQueue() {
    if (this.isProcessing || this.queue.length === 0) return;
  
    this.isProcessing = true;

    while (this.queue.length > 0) {
      const updateData = this.queue.shift();
      try {
        await this.handleUpdate(updateData)
      } catch (error) {
        console.error("Error processing update:", error)
      }
    }
  
    this.isProcessing = false;
  }

  handleUpdate(updateDate) {
    return Promise.resolve()
  }

  setUpdateHandler(handler) {
    this.handleUpdate = handler
  }

}

