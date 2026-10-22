import { createClient } from '@supabase/supabase-js'

export const SUPABASE_PROJECT_ID =
  import.meta.env.VITE_SUPABASE_PROJECT_ID || 'lomvdampiyqwicofxsxa'

export const SUPABASE_URL =
  import.meta.env.VITE_SUPABASE_URL || 'https://lomvdampiyqwicofxsxa.supabase.co'

export const SUPABASE_ANON_KEY =
  import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY ||
  import.meta.env.VITE_SUPABASE_ANON_KEY ||
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxvbXZkYW1waXlxd2ljb2Z4c3hhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTI2NDcyNzUsImV4cCI6MjEwODIyMzI3NX0.GJQytnoVLDvYJxu_TZ83a30K76ywHn3t2Se4CE_vmIw'

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
  },
})
