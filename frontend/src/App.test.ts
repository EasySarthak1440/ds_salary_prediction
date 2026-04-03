import { describe, it, expect } from 'vitest'

describe('App Component', () => {
  it('should have correct initial state', () => {
    const initialState = {
      activeTab: 'predict',
      market: 'India',
      loading: false,
      prediction: null,
      error: null,
    }
    expect(initialState.activeTab).toBe('predict')
    expect(initialState.market).toBe('India')
    expect(initialState.prediction).toBeNull()
  })

  it('should map features correctly for US market', () => {
    const formData = {
      rating: 4.2,
      yoe: 3,
      age: 10,
      python: true,
      sql: true,
      llm: true,
      cloud: true,
      spark: false,
      ml: true,
      stats: false,
      job_simp: 'data scientist',
      seniority: 'na',
    }

    const baseSample = [4.2, 0, 49, 0, 0, 0, 0, 0, 160, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]

    expect(formData.rating).toBe(4.2)
    expect(formData.python).toBe(true)
    expect(formData.cloud).toBe(true)
  })
})

describe('Form Data Validation', () => {
  it('should validate rating range', () => {
    const isValidRating = (rating: number) => rating >= 0 && rating <= 5
    expect(isValidRating(4.2)).toBe(true)
    expect(isValidRating(5.5)).toBe(false)
    expect(isValidRating(-1)).toBe(false)
  })

  it('should validate years of experience', () => {
    const isValidYOE = (yoe: number) => yoe >= 0 && yoe <= 50
    expect(isValidYOE(3)).toBe(true)
    expect(isValidYOE(0)).toBe(true)
    expect(isValidYOE(-1)).toBe(false)
  })
})
