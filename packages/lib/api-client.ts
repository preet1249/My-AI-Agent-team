/**
 * API Client - Shared across web and mobile
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000'

export class APIClient {
  private baseURL: string
  private token: string | null = null

  constructor(baseURL: string = API_URL) {
    this.baseURL = baseURL
  }

  setToken(token: string) {
    this.token = token
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(this.token && { Authorization: `Bearer ${this.token}` }),
      ...options.headers,
    }

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers,
    })

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`)
    }

    return response.json()
  }

  // Agent APIs
  async invokeAgent(agentName: string, prompt: string, metadata?: any) {
    return this.request('/api/agents/invoke', {
      method: 'POST',
      body: JSON.stringify({ agent_name: agentName, prompt, metadata }),
    })
  }

  async getAgents() {
    return this.request('/api/agents/list')
  }

  // Task APIs
  async getTaskStatus(taskId: string) {
    return this.request(`/api/tasks/${taskId}`)
  }

  async listTasks(params?: { user_id?: string; status?: string }) {
    const query = new URLSearchParams(params as any).toString()
    return this.request(`/api/tasks?${query}`)
  }

  // Sheet APIs
  async listSheets() {
    return this.request('/api/sheets/')
  }

  async getSheet(sheetId: string) {
    return this.request(`/api/sheets/${sheetId}`)
  }

  async createSheet(data: any) {
    return this.request('/api/sheets/', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  // Calendar APIs
  async listEvents(params?: { start_date?: string; end_date?: string }) {
    const query = new URLSearchParams(params as any).toString()
    return this.request(`/api/calendar/events?${query}`)
  }

  async createEvent(event: any) {
    return this.request('/api/calendar/events', {
      method: 'POST',
      body: JSON.stringify(event),
    })
  }
}

export const apiClient = new APIClient()
