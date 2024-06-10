import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
import time
import itertools
import urllib3
from expandedTLDs import expanded_TLDs
from expandedURLs import EXPANDED_URLS
from tqdm import tqdm


tld_variants=""
verbose = False

def generate_variants(url):
    global LETTER_REPLACEMENTS
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
    'z': ['a', 'x'],
    '0': ['O', 'o'],
    '1': ['I', 'l'],
    '2': ['ƻ', 'Ƨ'],
    '3': ['Ʒ', 'з'],
    '4': ['Ꮞ', 'Ꮿ'],
    '5': ['Ƽ', 'ƽ'],
    '6': ['б', 'ϐ'],
    '7': ['𝟟', '٧'],
    '8': ['𝟠', '۸'],
    '9': ['ϑ', '९']
    }

    

    domain_variants = set()
    for i in range(len(domain)):
        if domain[i].isalnum(): 
            for replacement in LETTER_REPLACEMENTS.get(domain[i].lower(), [domain[i].lower()]):
                variant = list(domain)
                variant[i] = replacement
                domain_variants.add("".join(variant))
                
    # Generate variants with multiple typos
    for typo_positions in itertools.combinations(range(len(domain)), 2):
        for replacements in itertools.product(*[LETTER_REPLACEMENTS.get(domain[pos].lower(), [domain[pos].lower()]) for pos in typo_positions]):
            variant = list(domain)
            for pos, replacement in zip(typo_positions, replacements):
                variant[pos] = replacement
            domain_variants.add("".join(variant))
    
    # Generate variants with added characters
    for i in range(len(domain) + 1):
        for char in LETTER_REPLACEMENTS.keys():
            variant = list(domain)
            variant.insert(i, char)
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

def check_url_availability(url, verbose=False):
    try:
        # Add a default scheme if not present
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        response = requests.get(url, timeout=10, verify=False)  # Disable SSL certificate verification and set timeout
        if verbose:
            print(f"Status code for {url}: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        if verbose:
            print(f"\033[31mURL Invalid: \033[37m{url}: {e}")
        return False

def main():
    global LETTER_REPLACEMENTS
    global tld_variants
    global verbose
    print('\033[33m██╗   ██╗██████╗ ██╗      \033[37m ██████╗ ██████╗ \033[36m██████╗ ██╗   ██╗\033[37m ██████╗ █████╗ ████████╗')
    print('\033[33m██║   ██║██╔══██╗██║      \033[37m██╔════╝██╔═══██╗\033[36m██╔══██╗╚██╗ ██╔╝\033[37m██╔════╝██╔══██╗╚══██╔══╝')
    print('\033[33m██║   ██║██████╔╝██║█████╗\033[37m██║     ██║   ██║\033[36m██████╔╝ ╚████╔╝ \033[37m██║     ███████║   ██║   ')
    print('\033[33m██║   ██║██╔══██╗██║╚════╝\033[37m██║     ██║   ██║\033[36m██╔═══╝   ╚██╔╝  \033[37m██║     ██╔══██║   ██║   ')
    print('\033[33m╚██████╔╝██║  ██║███████╗ \033[37m╚██████╗╚██████╔╝\033[36m██║        ██║   \033[37m╚██████╗██║  ██║   ██║   ')
    print('\033[33m ╚═════╝ ╚═╝  ╚═╝╚══════╝ \033[37m ╚═════╝ ╚═════╝ \033[36m╚═╝        ╚═╝   \033[37m ╚═════╝╚═╝  ╚═╝   ╚═╝   ')
    print('Created by Mio \nAtago66 on Github\n\n')

    time.sleep(2)

    input_url = input("Enter the URL:\033[35m ")

    is_TLDexpanded = input("\033[37mDo you want to expand the list of generated variants to all possible TLDs? (y/n): \n\033[31mWARNING: VERY SLOW AND MOSTLY USELESS!\n\033[32m")
    if is_TLDexpanded == 'y' or is_TLDexpanded == 'Y':
        tld_variants = expanded_TLDs
    elif is_TLDexpanded == 'n' or is_TLDexpanded == 'N':
        tld_variants = ['org', 'net', 'info']
    else:
        print("\033[31mInvalid input.\033[37m")
        main()
    
    is_URLexpanded = input("\033[37mDo you want to expand the list of generated variants to all possible URL typos? (y/n):\n\033[32m")
    if is_URLexpanded == 'y' or is_URLexpanded == 'Y':
        LETTER_REPLACEMENTS = EXPANDED_URLS
    elif is_URLexpanded == 'n' or is_URLexpanded == 'N':
        pass
    else:
        print("\033[31mInvalid input.\033[37m")
        main()

    if not verbose:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    verbose = input("\033[37mDo you want detailed output during testing? (y/n):\n\033[32m")
    if verbose == 'y' or verbose == 'Y':
         verbose = True
    elif verbose == 'n' or verbose == 'N':
        verbose = False
    else:
        print("\033[31mInvalid input.\033[37m")
        main()
    variants = generate_variants(input_url)
    if verbose:
        print("\n\033[36mGenerated Variants:\033[37m")
        for variant in variants:
            print(variant)

    valid_urls = []
    with ThreadPoolExecutor() as executor:
        future_to_url = {executor.submit(check_url_availability, variant, verbose): variant for variant in variants}
        for future in tqdm(as_completed(future_to_url), total=len(future_to_url), desc="\033[36mTesting URLs\033[35m", disable=verbose):
            url = future_to_url[future]
            try:
                if future.result():
                    valid_urls.append(url)
            except Exception as e:
                if verbose:
                    print(f"Exception occurred while checking URL {url}: {e}")

    print("\n\033[37mValid URLs:")
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
