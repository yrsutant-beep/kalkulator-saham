# ✅ Security Checklist - Pre-Deployment

Gunakan checklist ini sebelum merilis fitur baru atau update ke production.

---

## 📋 Pre-Deployment Checklist

### Input Validation ✓

- [ ] **Ticker Validation**
  - [ ] Format ticker divalidasi: `^[A-Z]{1,5}\.JK$`
  - [ ] Max length 10 karakter
  - [ ] Case-insensitive input diubah ke UPPERCASE
  - [ ] Whitespace di-strip
  
  ```python
  # Contoh implementasi
  def validate_ticker(ticker):
      clean = ticker.strip().upper()
      if not re.match(r'^[A-Z]{1,5}\.JK$', clean):
          raise ValueError("Invalid ticker format")
      return clean
  ```

- [ ] **Numeric Input Boundaries**
  - [ ] WACC: 0.5% - 20% ✓
  - [ ] Growth Rate: -10% - 30% ✓
  - [ ] PE Ratio: 1x - 100x ✓
  - [ ] PBV Ratio: 0.1x - 10x ✓
  
  ```python
  # Contoh implementasi
  if not (0.5 <= wacc <= 20):
      raise ValueError(f"WACC {wacc}% out of range")
  ```

- [ ] **String Input Sanitization**
  - [ ] Strip leading/trailing whitespace
  - [ ] Batasi panjang maksimal (255 char)
  - [ ] Blokir special chars: `< > " ' ; & | \`
  - [ ] Cegah path traversal: `.. / \`
  
  ```python
  # Contoh implementasi
  dangerous = ['<', '>', '"', "'", ';', '&', '|', '`']
  for char in dangerous:
      if char in user_input:
          raise ValueError(f"Invalid character: {char}")
  ```

---

### API Security ✓

- [ ] **yfinance Integration**
  - [ ] Timeout diset: 10 detik ✓
  - [ ] Max retries: 3 kali ✓
  - [ ] Graceful fallback ke manual input ✓
  - [ ] Error handling yang proper
  
  ```python
  # Contoh implementasi
  try:
      data = yf.Ticker(ticker).info
  except Exception as e:
      logger.error(f"yfinance error: {e}")
      print("⚠️ Data tidak tersedia, silakan input manual")
  ```

- [ ] **Rate Limiting**
  - [ ] API call tidak dibatasi (yfinance free)
  - [ ] Jika ada rate limit: implement backoff
  - [ ] Log untuk monitoring

---

### Data Protection ✓

- [ ] **Sensitive Data Handling**
  - [ ] API keys TIDAK di-hardcode
  - [ ] Passwords TIDAK di-log
  - [ ] Personal data TIDAK di-simpan
  - [ ] Use `.env` untuk secrets
  
  ```python
  # ❌ JANGAN
  api_key = "sk_live_12345"  # hardcoded
  logger.info(f"User {username}, password: {pwd}")
  
  # ✅ BOLEH
  api_key = os.getenv('API_KEY')
  logger.info(f"User {username} authenticated")
  ```

- [ ] **Output Escaping**
  - [ ] Special chars di-escape dalam output
  - [ ] Cegah XSS/Injection dalam display
  - [ ] Format uang dengan safe function
  
  ```python
  # ✅ AMAN
  output = f"Harga: Rp {harga:,.2f}"
  
  # ❌ TIDAK AMAN
  output = f"Harga: {user_input}"
  ```

---

### Error Handling ✓

- [ ] **User Error Messages**
  - [ ] Generic messages untuk user
  - [ ] TIDAK expose stack trace
  - [ ] TIDAK expose file paths
  - [ ] TIDAK expose database names
  
  ```python
  # ❌ JANGAN tampilkan ke user
  print(f"Database error: {db.connection.error}")
  
  # ✅ BOLEH tampilkan ke user
  print("⚠️ Koneksi gagal. Silakan coba lagi.")
  # Log detail error untuk debugging
  logger.error(f"DB connection failed: {db.error}", exc_info=True)
  ```

- [ ] **Exception Logging**
  - [ ] Full stack trace di-log ke file
  - [ ] Sensitive data DI-MASK dalam log
  - [ ] Log level sesuai severity
  
  ```python
  logger.exception("Unexpected error")  # Full traceback
  logger.error("API call failed")       # Error level
  logger.warning("Low disk space")      # Warning level
  ```

---

### File Operations ✓

- [ ] **File Size Limits**
  - [ ] Max file size: 100 MB
  - [ ] Check ukuran sebelum proses
  
  ```python
  if file_size > 100_000_000:  # 100MB
      raise ValueError("File terlalu besar")
  ```

- [ ] **File Extension Whitelist**
  - [ ] Allowed: `.py, .json, .md, .txt, .csv, .xlsx`
  - [ ] Blocked: `.exe, .bat, .sh, .cmd, .ps1, .dll, .so`
  
  ```python
  allowed = {'.py', '.json', '.md', '.txt', '.csv'}
  ext = filename.rsplit('.', 1)[-1].lower()
  if f'.{ext}' not in allowed:
      raise ValueError("File type not allowed")
  ```

- [ ] **Path Traversal Prevention**
  - [ ] Reject `..` dalam path
  - [ ] Reject `/` dan `\` dalam filename
  - [ ] Resolve ke absolute path
  
  ```python
  if '..' in filename or '/' in filename:
      raise ValueError("Invalid path")
  ```

---

### Dependency Security ✓

- [ ] **Third-party Libraries**
  - [ ] `requirements.txt` atau `pyproject.toml` updated
  - [ ] Verifikasi dependency sources
  - [ ] Check untuk known vulnerabilities
  
  ```bash
  # Check vulnerabilities
  pip install safety
  safety check
  ```

- [ ] **Package Versions**
  - [ ] Pin major versions
  - [ ] Allow patch updates
  - [ ] Test sebelum update
  
  ```
  # requirements.txt
  yfinance>=0.1.70,<0.2.0
  pandas>=1.3.0,<2.0.0
  ```

---

### Testing & Validation ✓

- [ ] **Unit Tests untuk Validation**
  ```python
  # test_validation.py
  def test_ticker_validation():
      # Valid cases
      assert validate_ticker("BBCA.JK") == "BBCA.JK"
      
      # Invalid cases
      with pytest.raises(ValueError):
          validate_ticker("bbca")
          validate_ticker("BBCA")
          validate_ticker("BBCAA.JK")
  ```

- [ ] **Boundary Testing**
  ```python
  def test_wacc_boundaries():
      # Min value
      assert validate_wacc(0.5) == 0.5
      # Max value
      assert validate_wacc(20.0) == 20.0
      # Out of range
      with pytest.raises(ValueError):
          validate_wacc(0.1)
          validate_wacc(25.0)
  ```

- [ ] **Security Test Cases**
  - [ ] Test dengan input berbahaya
  - [ ] Test path traversal attempts
  - [ ] Test oversized files
  - [ ] Test invalid file types
  
  ```python
  def test_dangerous_inputs():
      with pytest.raises(ValueError):
          sanitize_text("<script>alert('xss')</script>")
          validate_filename("../../../etc/passwd")
  ```

---

### Code Review ✓

- [ ] **Security Review Checklist**
  - [ ] [ ] Tidak ada hardcoded secrets
  - [ ] [ ] Tidak ada command injection risks
  - [ ] [ ] Tidak ada SQL injection risks
  - [ ] [ ] Tidak ada XXE risks
  - [ ] [ ] Input validation pada semua endpoints
  - [ ] [ ] Output encoding proper
  - [ ] [ ] Error handling tidak expose info
  - [ ] [ ] Authentication/Authorization jelas
  - [ ] [ ] Logging tidak log sensitive data

- [ ] **Code Quality**
  - [ ] Type hints lengkap
  - [ ] Docstrings jelas
  - [ ] No unused imports
  - [ ] Proper exception handling
  - [ ] No bare except clauses

---

### Environment & Configuration ✓

- [ ] **Environment Files**
  - [ ] `.env` adalah template (`.env.example`)
  - [ ] `.env` di-gitignore ✓
  - [ ] No secrets dalam `.env.example`
  - [ ] Documentation untuk setiap env var
  
  ```
  # .gitignore
  .env
  .env.local
  .env.*.local
  *.key
  *.pem
  ```

- [ ] **Configuration Management**
  - [ ] Config terpisah dari code
  - [ ] Different config untuk dev/prod
  - [ ] Debug mode OFF di production
  - [ ] Log level TIDAK debug di prod
  
  ```python
  # ❌ JANGAN di production
  DEBUG = True
  LOG_LEVEL = "DEBUG"
  
  # ✅ BOLEH di production
  DEBUG = False
  LOG_LEVEL = "INFO"
  ```

---

### Logging & Monitoring ✓

- [ ] **Logging Configuration**
  - [ ] Log file location ditentukan
  - [ ] Log rotation diatur (10MB default)
  - [ ] Log level appropriate untuk environment
  - [ ] Sensitive data di-mask dalam log
  
  ```python
  logging.basicConfig(
      level=logging.INFO,
      format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
      handlers=[
          logging.FileHandler('logs/app.log'),
          logging.StreamHandler()
      ]
  )
  ```

- [ ] **Sensitive Data Masking**
  ```python
  # ❌ JANGAN log ini
  logger.info(f"API key: {api_key}")
  logger.info(f"Password: {password}")
  
  # ✅ MASK sensitive data
  masked_key = api_key[:4] + "****"
  logger.info(f"API key: {masked_key}")
  ```

- [ ] **Audit Trail**
  - [ ] Important actions di-log
  - [ ] Timestamps accurate
  - [ ] User/source identity tracked
  - [ ] Changes are immutable

---

### Performance & DoS Prevention ✓

- [ ] **Timeout Configuration**
  - [ ] API calls: 10 detik timeout
  - [ ] File uploads: size limit 100MB
  - [ ] String inputs: length limit 255 char
  
  ```python
  requests.get(url, timeout=10)
  if file_size > 100_000_000:
      raise ValueError("File too large")
  ```

- [ ] **Resource Limits**
  - [ ] Memory usage monitored
  - [ ] CPU usage monitored
  - [ ] Concurrent requests limited (jika needed)

---

### Documentation ✓

- [ ] **Security Documentation**
  - [ ] [ ] `SECURITY.md` up-to-date
  - [ ] [ ] `security-rules.json` reviewed
  - [ ] [ ] Security checklist completed
  - [ ] [ ] Deployment guide clear
  - [ ] [ ] Emergency contacts listed

- [ ] **Comments & Docstrings**
  ```python
  def validate_ticker(ticker: str) -> str:
      """
      Validasi format ticker saham Indonesia.
      
      Args:
          ticker: Ticker code (contoh: BBCA.JK)
      
      Returns:
          str: Validated ticker uppercase
      
      Raises:
          ValueError: Jika format tidak valid
      """
  ```

---

## 🚀 Pre-Release Checklist

Sebelum release ke production:

- [ ] **Security tests passed**
  ```bash
  pytest test_security.py -v
  pytest test_validation.py -v
  ```

- [ ] **Code review completed**
  - [ ] Security review passed
  - [ ] Code quality check passed

- [ ] **Environment configured**
  - [ ] `.env` file setup
  - [ ] DEBUG = False
  - [ ] LOG_LEVEL = INFO (or WARNING)

- [ ] **Dependencies updated**
  ```bash
  pip list --outdated
  pip-audit  # Check untuk vulnerabilities
  ```

- [ ] **Logging verified**
  - [ ] Log files created
  - [ ] Log rotation working
  - [ ] No sensitive data in logs

- [ ] **Documentation complete**
  - [ ] Security.md reviewed
  - [ ] CHANGELOG updated
  - [ ] README updated

---

## 📋 Post-Deployment

- [ ] **Monitoring enabled**
  - [ ] Log aggregation working
  - [ ] Error alerts configured
  - [ ] Performance metrics tracked

- [ ] **Incident response ready**
  - [ ] On-call contacts listed
  - [ ] Escalation process clear
  - [ ] Rollback procedure ready

- [ ] **Regular maintenance**
  - [ ] Security patches monitored
  - [ ] Dependency updates tracked
  - [ ] Quarterly security review scheduled

---

## 🔍 Automated Security Checks

Konfigurasi CI/CD untuk automated checks:

```yaml
# .github/workflows/security.yml
name: Security Checks
on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Run bandit (find security issues)
        run: |
          pip install bandit
          bandit -r . -f json -o bandit-report.json
      
      - name: Run safety (check dependencies)
        run: |
          pip install safety
          safety check --json
      
      - name: Run pytest
        run: |
          pytest test_validation.py -v
          pytest test_security.py -v
```

---

## 📞 Security Incident Response

Jika ditemukan kerentanan:

1. **Jangan disclose publik** - Report ke security team
2. **Document the issue** - Buat detailed report
3. **Create patch** - Develop fix urgently
4. **Test patch** - Verify fix works
5. **Deploy patch** - Roll out with security update
6. **Post-mortem** - Analyze root cause

---

## ✅ Completion Status

**Last Checklist Date:** 2026-09-18  
**Checklist Version:** 1.0  
**Responsible:** Development Team

---

**Remember:** Security is not a destination, it's a continuous process. Review this checklist regularly and update based on new threats and best practices.
