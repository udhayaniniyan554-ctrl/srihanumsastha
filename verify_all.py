import os

project_dir = r"C:\Users\user\.gemini\antigravity\scratch\srihanumsastha-catalogue"
for fname in ['index.html', 'category.html', 'contact.html']:
    with open(os.path.join(project_dir, fname), 'r', encoding='utf-8') as f:
        html = f.read()
    
    assert 'Sri Hanum Sastha Enterprises' in html, f'{fname}: Missing Company'
    assert '173, First Floor, KK Lane Street, Avinashi Road, Coimbatore' in html, f'{fname}: Missing Address'
    assert 'tel:9688727284' in html, f'{fname}: Missing tel:9688727284'
    assert 'tel:8695706013' in html, f'{fname}: Missing tel:8695706013'
    assert 'Call 9688727284' in html, f'{fname}: Missing Call 9688727284 button'
    assert 'Call 8695706013' in html, f'{fname}: Missing Call 8695706013 button'
    assert 'Prices may change. Please contact us to confirm current prices and availability.' in html, f'{fname}: Missing disclaimer'
    
    for word in ['cart', 'checkout', 'payment', 'login', 'register']:
        assert f'href="/{word}' not in html, f'{fname}: Found /{word}'
        assert f'id="{word}' not in html, f'{fname}: Found id={word}'

print("All business details, phone buttons, addresses, disclaimer, and catalogue-only restrictions verified across all HTML files!")
