import requests
from urllib.parse import urlparse
import time
from expandedTLDs import expanded_TLDs
# Define common letter replacements

tld_variants=""

def generate_variants(url):
    global tld_variants
    if not urlparse(url).scheme:
        url = 'http://' + url
    
    # Extract the domain part of the URL
    parsed_url = urlparse(url)
    domain_parts = parsed_url.netloc.split('.')

    if len(domain_parts) > 1:
        domain = domain_parts[0]
        tld = '.'.join(domain_parts[1:])
    else:
        domain = parsed_url.netloc
        tld = ''

    LETTER_REPLACEMENTS = {
    'a': ['s', 'q', 'z', 'o'],
    'b': ['v', 'g', 'n'],
    'c': ['x', 'v', 'f'],
    'd': ['s', 'f', 'e'],
    'e': ['w', 'r', 'd', '3'],
    'f': ['d', 'g', 'r'],
    'g': ['f', 'h', 'b'],
    'h': ['g', 'j', 'y'],
    'i': ['u', 'o', 'k', 'e', '1'],
    'j': ['h', 'k', 'u'],
    'k': ['j', 'l', 'i'],
    'l': ['k', 'o', 'i', '1'],
    'm': ['n', 'j'],
    'n': ['b', 'm', 'j'],
    'o': ['i', 'p', 'l', 'a', 'u', '0'],
    'p': ['o', 'l'],
    'q': ['w', 'a'],
    'r': ['e', 't', 'f'],
    's': ['a', 'd', 'w'],
    't': ['r', 'y', 'g'],
    'u': ['y', 'i', 'j'],
    'v': ['c', 'b', 'g'],
    'w': ['q', 'e', 's'],
    'x': ['z', 'c', 's'],
    'y': ['t', 'u', 'h'],
    'z': ['a', 'x']
    }

    domain_variants = set()
    for i in range(len(domain)):
        if domain[i].isalnum():  # Only generate variants for alphanumeric characters
            for replacement in LETTER_REPLACEMENTS.get(domain[i].lower(), [domain[i].lower()]):
                variant = list(domain)
                variant[i] = replacement
                domain_variants.add("".join(variant))

    # Generate variants with different TLDs
    if tld:
        tld_variants.insert(0, tld)  # Include the original TLD if it exists
    variants = []
    for domain_variant in domain_variants:
        for tld_variant in tld_variants:
            variant = f"{domain_variant}.{tld_variant}" if tld_variant else domain_variant
            variants.append(variant)
    
    return variants

def check_url_availability(url):
    try:
        # Add a default scheme if not present
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        response = requests.get(url, timeout=10, verify=False)  # Disable SSL certificate verification and set timeout
        return response.status_code == 200
    except Exception as e:
        print(f"\033[31mURL Invalid: \033[37m{url}: {e}")
        return False

def main():
    global tld_variants
    print('\033[33m██╗   ██╗██████╗ ██╗      \033[37m ██████╗ ██████╗ \033[36m██████╗ ██╗   ██╗\033[37m ██████╗ █████╗ ████████╗')
    print('\033[33m██║   ██║██╔══██╗██║      \033[37m██╔════╝██╔═══██╗\033[36m██╔══██╗╚██╗ ██╔╝\033[37m██╔════╝██╔══██╗╚══██╔══╝')
    print('\033[33m██║   ██║██████╔╝██║█████╗\033[37m██║     ██║   ██║\033[36m██████╔╝ ╚████╔╝ \033[37m██║     ███████║   ██║   ')
    print('\033[33m██║   ██║██╔══██╗██║╚════╝\033[37m██║     ██║   ██║\033[36m██╔═══╝   ╚██╔╝  \033[37m██║     ██╔══██║   ██║   ')
    print('\033[33m╚██████╔╝██║  ██║███████╗ \033[37m╚██████╗╚██████╔╝\033[36m██║        ██║   \033[37m╚██████╗██║  ██║   ██║   ')
    print('\033[33m ╚═════╝ ╚═╝  ╚═╝╚══════╝ \033[37m ╚═════╝ ╚═════╝ \033[36m╚═╝        ╚═╝   \033[37m ╚═════╝╚═╝  ╚═╝   ╚═╝   ')
    print('Created by Mio \nAtago66 on Github\n\n')
    time.sleep(2)
    input_url = input("Enter the URL:\033[35m ")
    is_expanded = input("\033[37mDo you want to expand the list of generated variants to all possible TLDs? (y/n): \n\033[31mWARNING: VERY SLOW AND MOSTLY USELESS!\n\033[32m")
    if is_expanded == 'y' or is_expanded == 'Y':
        tld_variants = expanded_TLDs
    elif is_expanded == 'n' or is_expanded == 'N':
        tld_variants = ['org', 'net', 'info']
    else:
        print("\033[31mInvalid input. Please enter 'y' or 'n'.\033[37m")
        main()
    variants = generate_variants(input_url)
    print("\n\033[36mGenerated Variants:\033[37m")
    for variant in variants:
        print(variant)

    valid_urls = []
    for variant in variants:
        print(f"\033[33mTesting: \033[37m{variant}")
        if check_url_availability(variant):
            valid_urls.append(variant)

    print("\nValid URLs:")
    if valid_urls:
        for url in valid_urls:
            print(url)
        print('\n')
    else:
        print("None")
        print('\n')
    main()

if __name__ == "__main__":
    main()