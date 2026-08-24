import sys, os
print('cwd=', os.getcwd())
print('sys.path[0]=', sys.path[0])
print('len(sys.path)=', len(sys.path))
print('\nfirst 10 sys.path entries:')
for p in sys.path[:10]:
    print(p)

print('\nattempt import app:')
try:
    import app
    print('app imported')
except Exception as e:
    print('import app failed:', type(e), e)
