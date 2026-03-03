---
description: Systematically debug and fix errors with comprehensive methodology
---

# How to systematically debug and fix errors

Please systematically debug and resolve the error: $ARGUMENTS.

Follow this comprehensive debugging methodology:

## 1. Error Information Gathering

1. **Collect error details:**
   ```bash
   # Check application logs
   tail -f logs/app.log
   # Check system logs
   journalctl -u service-name -f
   ```

2. **Document the error:**
   - Complete error message and stack trace
   - Error code (if applicable)
   - When it occurs (timing, conditions, frequency)
   - Environment (dev, staging, prod)
   - Recent changes that might be related

## 2. Reproduce the Error

1. **Create minimal reproduction:**
   - Isolate the failing code
   - Remove unnecessary dependencies
   - Document exact steps to trigger

2. **Test systematically:**
   ```bash
   # Run with debug mode
   DEBUG=* npm start
   # Run with verbose logging
   npm run dev -- --verbose
   ```

## 3. Analyze Stack Trace

1. **Read stack trace from bottom to top**
2. **Identify the exact error location**
3. **Trace the execution path**
4. **Look for common patterns:**
   - Null/undefined references
   - Type mismatches
   - Array out of bounds
   - Missing properties

## 4. Investigate Code Context

1. **Check recent changes:**
   ```bash
   # View recent commits affecting the file
   git log -p path/to/failing/file.ts
   # Check blame to see who changed what
   git blame path/to/failing/file.ts
   ```

2. **Examine the failing code:**
   - Variable values at error time
   - Function parameters and returns
   - State before and after

## 5. Form and Test Hypotheses

### Common causes to check:
- **Data issues:** null/undefined, type mismatches
- **Timing issues:** race conditions, async problems
- **Resource issues:** memory leaks, connection limits
- **Logic errors:** off-by-one, edge cases
- **External failures:** API down, network issues

## 6. Debug with Tools

1. **Use appropriate debugger:**
   ```bash
   # Node.js debugging
   node --inspect-brk app.js
   # Browser debugging
   debugger; // Add breakpoint in code
   ```

2. **Add strategic logging:**
   ```javascript
   console.log('State before:', { data });
   // Failing operation
   console.log('State after:', { result });
   ```

## 7. Systematic Investigation

### Data validation:
```bash
# Validate input data
console.log(JSON.stringify(inputData, null, 2));
# Test edge cases
testWithEmptyData();
testWithLargeData();
testWithInvalidData();
```

### Check dependencies:
```bash
# Verify versions
npm list --depth=0
# Check for vulnerabilities
npm audit
# Test connections
curl -I https://api.example.com/health
```

### Resource monitoring:
```bash
# Memory usage
node --expose-gc --trace-gc app.js
# CPU profiling
node --prof app.js
# Network monitoring
netstat -an | grep ESTABLISHED
```

## 8. Implement the Fix

1. **Address root cause, not symptoms**
2. **Add proper error handling:**
   ```javascript
   try {
     // Fixed code with validation
     if (!data || !data.required) {
       throw new Error('Missing required data');
     }
     return processData(data);
   } catch (error) {
     logger.error('Processing failed:', error);
     throw error;
   }
   ```

3. **Consider edge cases and defensive programming**

## 9. Test and Validate

1. **Test the fix thoroughly:**
   ```bash
   # Run unit tests
   npm test -- --watch path/to/test
   # Run integration tests
   npm run test:integration
   # Test edge cases manually
   ```

2. **Verify no regressions:**
   ```bash
   npm run test:all
   npm run lint
   npm run type-check
   ```

## 10. Prevent Future Issues

1. **Add tests for the bug:**
   ```javascript
   test('handles edge case that caused bug', () => {
     expect(() => buggyFunction(null)).toThrow();
     expect(buggyFunction(validData)).toBe(expected);
   });
   ```

2. **Improve error handling and monitoring**
3. **Document the fix and lessons learned**
4. **Update code comments with context**

## Best Practices

- **Keep detailed notes** throughout the debugging process
- **Use version control** to track changes while debugging
- **Test incrementally** after each change
- **Consider the wider impact** of both the error and fix
- **Share knowledge** with the team to prevent similar issues
- **Add monitoring** to catch similar errors early

## Quick Debugging Checklist

- [ ] Error message and stack trace collected
- [ ] Error reproduced consistently
- [ ] Root cause identified
- [ ] Fix implemented with error handling
- [ ] Tests added to prevent regression
- [ ] Documentation updated
- [ ] Monitoring in place
