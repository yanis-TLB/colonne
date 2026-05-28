const jwt = require('jsonwebtoken');
const secret = '4DLFGr+agdoPvQERwVBxv5BKzsqtdJCpWA1K22ghfSD1o/K4D+vS7kmZ9GCUR78Lxj7wv6GFuidSVmLJvvm4xQ==';
const token = jwt.sign(
  { role: 'anon', iss: 'supabase', iat: 1741132800, exp: 1898899200 },
  secret,
  { algorithm: 'HS256' }
);
console.log(token);