import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://ozjhgxwtrawprbjxpvru.supabase.co'
const supabaseKey = 'sb_publishable_XBx6yCr0-k95bH0wxs6ptg_i31ymnon'

export const supabase = createClient(supabaseUrl, supabaseKey)
