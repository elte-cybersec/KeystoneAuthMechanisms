import qrcode
### change the secret variable!
secret = 'YOUR_TOTP_SECRET'
uri = 'otpauth://totp/{name}?secret={secret}&issuer={issuer}'.format(
    name='USERNAME',
    secret=secret,
    issuer='Keystone')

img = qrcode.make(uri)
img.save('totp.png')
