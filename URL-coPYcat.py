import requests
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
import time
import itertools
import urllib3
from expandedTLDs import expanded_TLDs
from expandedURLs import EXPANDED_URLS
import tkinter as tk
from tkinter import ttk, StringVar,  Text
from threading import Thread

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
    
def create_gui():
    def check_urls_thread(variants, verbose, result_text, root):
        global tld_variants
        global LETTER_REPLACEMENTS
        input_url = url_entry.get()
        is_TLDexpanded = tld_variants_var.get()
        is_URLexpanded = url_variants_var.get()
        verbose = verbose_var.get()

        if is_TLDexpanded:
            tld_variants = expanded_TLDs
        else:
            tld_variants = ['org', 'net', 'info']

        if is_URLexpanded:
            LETTER_REPLACEMENTS = EXPANDED_URLS
        else:
            LETTER_REPLACEMENTS = {}

        if not verbose:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        if input_url == "":
            return
            
        variants = generate_variants(input_url)

        valid_urls = []

        class ConsoleOutput:
            def __init__(self, text_widget):
                self.text_widget = text_widget

            def write(self, string):
                self.text_widget.insert(tk.END, string)
                self.text_widget.see(tk.END)

            def flush(self):
                pass

        class TqdmToTk:
            def __init__(self, total, root):
                self.total = total
                self.start_time = time.time()
                self.progress = 0
                self.progressbar = ttk.Progressbar(root, length=500, mode='determinate')
                self.progressbar.place(x=50, y=160)
                self.progressbar['maximum'] = total
                self.label_var = StringVar()
                self.label = ttk.Label(root, textvariable=self.label_var)
                self.label.pack()
                self.update_thread = Thread(target=self.update_eta)
                self.update_thread.start()
                self.valid_urls_text = Text(root)
                if verbose:
                    self.console_output = tk.Text(root, height=10)
                    self.console_output.place(x=0, y=400)
                    sys.stdout = ConsoleOutput(self.console_output)


            def update_eta(self):
                while self.progress < self.total:
                    elapsed_time = time.time() - self.start_time
                    eta = (self.total - self.progress) * (elapsed_time / self.progress) if self.progress > 0 else 0
                    self.label_var.set(f"Processed: {self.progress}/{self.total}, ETA: {eta:.0f} seconds")
                    self.progress += 1
                    time.sleep(0.5) 

            def update_to(self, b):
                self.progress = b
                self.progressbar['value'] = self.progress
                root.update_idletasks()  # Update the GUI

            def close(self):
                self.progressbar.destroy()
                self.label.destroy()
                self.update_thread.join()  # Wait for the update thread to finish

        with ThreadPoolExecutor() as executor:
            future_to_url = {executor.submit(check_url_availability, variant, verbose): variant for variant in variants}
            checked_urls = 0
            pbar = TqdmToTk(total=len(future_to_url), root=root)
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    if future.result():
                        valid_urls.append(url)
                        # Schedule GUI update on the main thread
                        root.after(0, lambda url=url: (result_text.config(state=tk.NORMAL), result_text.insert(tk.END, f"{url}\n"), result_text.config(state=tk.DISABLED)))
                except Exception as e:
                    if verbose:
                        print(f"Exception occurred while checking URL {url}: {e}")
                finally:
                    checked_urls += 1
                    pbar.update_to(checked_urls)
            pbar.close()
    root = tk.Tk()
    root.title("URL-coPYcat - v1.2.0")
    w = 600
    h = 400
    ws = root.winfo_screenwidth() 
    hs = root.winfo_screenheight() 
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))

    # URL Entry
    url_label = ttk.Label(root, text="Enter a URL to be tested:")
    url_label.pack()
    url_entry = ttk.Entry(root)
    url_entry.pack()

    # TLD Expanded Checkbutton
    tld_variants_var = tk.BooleanVar()
    tld_variants_checkbutton = ttk.Checkbutton(root, text="Expand TLD Variants", variable=tld_variants_var)
    tld_variants_checkbutton.pack()

    # URL Variants Checkbutton
    url_variants_var = tk.BooleanVar()
    url_variants_checkbutton = ttk.Checkbutton(root, text="Expand Character Variation", variable=url_variants_var)
    url_variants_checkbutton.pack()

    # Verbose Checkbutton
    verbose_var = tk.BooleanVar()
    def resize_root():
        if verbose_var.get():
            root.geometry("600x600")  # Increase the height if verbose is enabled
        else:
            root.geometry("600x400")  # Decrease the height if verbose is disabled
    verbose_checkbutton = ttk.Checkbutton(root, text="Verbose Output", variable=verbose_var, command=resize_root)
    verbose_checkbutton.pack()

    
        

    # Check URLs Button
    check_button = ttk.Button(root, text="Test URL", command=lambda: Thread(target=check_urls_thread, args=(url_variants_var.get(), verbose_var.get(), result_text, root)).start())
    check_button.pack()

    # Create Text widget
    result_text = tk.Text(root, height=10)
    result_text.place(x=0, y=200)
    result_text.config(state=tk.DISABLED)

    root.mainloop()

if __name__ == "__main__":
    create_gui()

