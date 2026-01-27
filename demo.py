#!/usr/bin/env python3
"""
Enhanced VesselReID dataset downloader.
"""

import os
import json
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import sys
import urllib.request as request
import urllib.error
import http.cookiejar as cookielib
import gzip
import gc

# Retry decorator for handling network failures
def retry_on_failure(max_retries=3, delay=1, backoff=2):
    """
    Decorator for retrying function on exceptions with exponential backoff
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
                    retries += 1
                    if retries == max_retries:
                        print(f"Failed after {max_retries} attempts: {e}")
                        raise
                    print(f"\nRetry {retries}/{max_retries} after error: {e}")
                    time.sleep(current_delay)
                    current_delay *= backoff
            return None
        return wrapper
    return decorator

# Simple progress indicator
class ProgressBar:
    def __init__(self, total, description="Progress", bar_length=50):
        self.total = total
        self.description = description
        self.bar_length = bar_length
        self.current = 0
        self.start_time = time.time()
        
    def update(self, n=1):
        self.current += n
        elapsed = time.time() - self.start_time
        percent = self.current / self.total
        filled_length = int(self.bar_length * percent)
        bar = '█' * filled_length + '─' * (self.bar_length - filled_length)
        
        # Calculate ETA
        if self.current > 0 and elapsed > 0:
            speed = self.current / elapsed
            eta = (self.total - self.current) / speed if speed > 0 else 0
            eta_str = f"ETA: {eta:.1f}s"
        else:
            speed = 0
            eta_str = "ETA: --"
        
        sys.stdout.write(f'\r{self.description}: [{bar}] {percent:.1%} | {self.current}/{self.total} | Speed: {speed:.2f} img/s | {eta_str}')
        sys.stdout.flush()
        
    def close(self):
        sys.stdout.write('\n')
        sys.stdout.flush()

class VesselReIDDownloader:
    def __init__(self, 
                 annotation_path: str, 
                 save_path: str, 
                 proxy_type: str = 'no',
                 max_workers: int = 5,
                 timeout: int = 30):
        """
        Initialize the downloader with configuration parameters
        """
        self.annotation_path = annotation_path
        self.save_path = Path(save_path)
        self.proxy_type = proxy_type
        self.max_workers = max_workers
        self.timeout = timeout
        
        # Statistics tracking
        self.stats = {
            'total': 0,
            'downloaded': 0,
            'skipped': 0,
            'failed': 0
        }
        
    def select_proxy(self, proxy_type='socks-client'):
        """Return proxy configuration based on type (same as original script)"""
        proxies = {}
        if proxy_type == 'http':
            proxies = {
                'https': 'https://127.0.0.1:2173',
                'http': 'http://127.0.0.1:2173'
            }
        elif proxy_type == 'socks-remote':
            proxies = {
                'socks5': 'socks5://user:pass@host:port',
                'socks5': 'socks5://user:pass@host:port'
            }
        elif proxy_type == 'socks-client':
            proxies = {
                'http': 'socks5://127.0.0.1:2080',
                'https': 'socks5://127.0.0.1:2080'
            }
        return proxies
    
    @retry_on_failure(max_retries=5, delay=2, backoff=2)
    def _download_single_image(self, url: str, save_path: Path) -> bool:
        """
        Download a single image using urllib (like original script)
        """
        # Check if file already exists
        if save_path.exists():
            return True
            
        try:
            # Get proxy settings
            proxies = self.select_proxy(self.proxy_type)
            agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36"
            headers = {'user-agent': agent}
            
            # Setup opener with proxy (like original script)
            cookie = cookielib.CookieJar()
            opener = request.build_opener(
                request.ProxyHandler(proxies), 
                request.HTTPCookieProcessor(cookie)
            )
            request.install_opener(opener)
            
            # Create request
            req = request.Request(url, headers=headers)
            
            # Download with timeout
            response = request.urlopen(req, timeout=self.timeout)
            
            # Read and save data
            data = response.read()
            
            # Create directory if needed
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save file
            with open(save_path, 'wb') as f:
                f.write(data)
            
            # Cleanup
            response.close()
            
            # Verify file was written
            return save_path.stat().st_size > 0
                
        except urllib.error.URLError as e:
            print(f"\nConnection error for {url}: {e.reason}")
            raise
        except Exception as e:
            print(f"\nError downloading {url}: {e}")
            # Clean up potentially corrupted file
            if save_path.exists():
                save_path.unlink(missing_ok=True)
            return False
            
    def _process_image(self, img_data: dict, save_root: Path) -> tuple:
        """
        Process a single image entry from the annotation file
        """
        img_name = img_data['name']
        download_url = img_data['url']
        split_info = img_data['split']
        
        datasets_type = ['normal', 'extra']
        success = False
        
        for dt in datasets_type:
            if split_info.get(dt):
                # Create save path
                pth = save_root / f"{dt}_split" / split_info[dt] / img_name
                
                # Download the image
                success = self._download_single_image(download_url, pth)
                
                if success:
                    if pth.exists():
                        self.stats['downloaded'] += 1
                    else:
                        self.stats['skipped'] += 1
                else:
                    self.stats['failed'] += 1
                    
                break  # Only need to download once per image
        
        return success, img_name
    
    def load_annotations(self) -> dict:
        """
        Load and validate the annotation JSON file
        """
        if not Path(self.annotation_path).exists():
            raise FileNotFoundError(f"Annotation file not found: {self.annotation_path}")
            
        with open(self.annotation_path, 'r') as f:
            data = json.load(f)
            
        if 'images' not in data:
            raise ValueError("Invalid annotation file format: 'images' key not found")
            
        return data
    
    def download_all(self) -> dict:
        """
        Download all images with concurrent processing
        """
        # Load annotation data
        data = self.load_annotations()
        images = data['images']
        self.stats['total'] = len(images)
        
        print(f"Starting download of {self.stats['total']} images")
        print(f"Save directory: {self.save_path}")
        print(f"Concurrent workers: {self.max_workers}")
        print(f"Proxy type: {self.proxy_type}")
        print("-" * 50)
        
        start_time = time.time()
        
        # Create progress bar
        progress = ProgressBar(total=self.stats['total'], description="Downloading")
        
        # Use ThreadPoolExecutor for concurrent downloads
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all download tasks
            future_to_img = {
                executor.submit(self._process_image, img, self.save_path): img
                for img in images
            }
            
            # Process completed tasks
            completed = 0
            for future in as_completed(future_to_img):
                try:
                    success, img_name = future.result()
                    completed += 1
                    progress.update(1)
                    
                except Exception as e:
                    print(f"\nUnexpected error: {e}")
                    self.stats['failed'] += 1
                    completed += 1
                    progress.update(1)
        
        progress.close()
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        
        # Print summary
        print("\n" + "=" * 50)
        print("DOWNLOAD SUMMARY")
        print("=" * 50)
        print(f"Total images:    {self.stats['total']}")
        print(f"Successfully downloaded: {self.stats['downloaded']}")
        print(f"Skipped (already existed): {self.stats['skipped']}")
        print(f"Failed:          {self.stats['failed']}")
        print(f"Time elapsed:    {elapsed_time:.2f} seconds")
        if self.stats['downloaded'] > 0:
            print(f"Average speed:   {self.stats['downloaded']/elapsed_time:.2f} img/sec")
        
        return self.stats

def main():
    parser = argparse.ArgumentParser(
        description='VesselReID dataset downloader using urllib'
    )
    
    parser.add_argument('--pth',
                        help='Path to the dataset annotation JSON file',
                        type=str,
                        default='./VesselReID.json')
    
    parser.add_argument('--save_pth',
                        help='Directory to save downloaded dataset',
                        type=str,
                        default='./VesselReID')
    
    parser.add_argument('--proxy',
                        help='Proxy type: no, http, socks-client, socks-remote',
                        type=str,
                        default='no',
                        choices=['no', 'http', 'socks-client', 'socks-remote'])
    
    parser.add_argument('--workers',
                        help='Number of concurrent download workers',
                        type=int,
                        default=5)
    
    parser.add_argument('--timeout',
                        help='Request timeout in seconds',
                        type=int,
                        default=30)
    
    args = parser.parse_args()
    
    # Initialize downloader
    downloader = VesselReIDDownloader(
        annotation_path=args.pth,
        save_path=args.save_pth,
        proxy_type=args.proxy,
        max_workers=args.workers,
        timeout=args.timeout
    )
    
    try:
        # Start download process
        stats = downloader.download_all()
        
        # Save download statistics
        stats_file = Path(args.save_pth) / 'download_stats.json'
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        print(f"\nStatistics saved to: {stats_file}")
        
    except KeyboardInterrupt:
        print("\nDownload interrupted by user")
    except Exception as e:
        print(f"\nFatal error: {e}")

if __name__ == '__main__':
    main()
