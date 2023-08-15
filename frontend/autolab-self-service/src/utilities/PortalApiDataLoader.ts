import {reactive} from "vue"

interface PortalApiDataLoaderState<T> {
  loading: boolean
  loaded: boolean
  error: string | null
  data: T | null
}

interface PortalApiDataLoaderOptions {
  method: string
  body?: any
  headers?: any
}

export class PortalApiDataLoader<T> {
  endpoint: string
  method: string
  state: PortalApiDataLoaderState<T>

  constructor(endpoint: string, method?: string) {
    this.endpoint = endpoint
    this.method = method || 'GET'
    this.state = reactive({
      loading: false,
      loaded: false,
      error: null,
      data: null,
    }) as PortalApiDataLoaderState<T>
  }

  fetch(body?: any, json?: boolean, headers?: object) {
    this.state.loading = true
    // Define fetch options
    const options = {
      method: this.method,
      headers: {},
      body: undefined,
    } as PortalApiDataLoaderOptions
    // Add a body if it was passed
    if (typeof body !== typeof undefined) {
      options.body = body
    }
    // Default to JSON true
    if (typeof json === typeof undefined) {
      json = true
    }
    // If headers were provided, add them
    if (typeof headers !== typeof undefined) {
      options.headers = headers
    }
    // Add a header for JSON if the input format is JSON
    if (json) {
      options.headers['Content-Type'] = 'application/json'
      options.body = JSON.stringify(options.body)
    }

    fetch(this.endpoint, options)
      .then(response => response.json())
      .then(data => {
        if (data.success === false) {
          throw new Error(data.error)
        }
        this.state.data = data.data
        this.state.loaded = true
        this.state.error = null
      })
      .catch((error) => {
        this.state.error = error.message
      })
      .finally(() => {
        this.state.loading = false
      })
  }

}
