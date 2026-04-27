import Joi from 'joi'

const schema = Joi.object({
  VITE_ENV: Joi.string().valid('development', 'production').required(),
}).unknown(true)

const { error, value } = schema.validate(import.meta.env, { abortEarly: false })

if (error) {
  throw new Error(`Invalid frontend env: ${error.message}`)
}

export const ENV = value.VITE_ENV
export const isDevelopment = ENV === 'development'
