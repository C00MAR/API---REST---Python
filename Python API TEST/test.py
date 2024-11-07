from requests import Session
from typing import Optional, List, Dict
import threading
from queue import Queue, Empty
from dataclasses import dataclass
from datetime import datetime

@dataclass
class EmailResult:
    email: str
    token: Optional[str] = None
    user_id: Optional[str] = None
    status: str = "pending"
    error: Optional[str] = None
    timestamp: str = str(datetime.now())

class ThreadedTEST:
    def __init__(
            self, api_key: str = "15e97ca6-037e-4527-9bc5-a0479fbe0f9e",
            base_url: str = "https://2sqsobpu3f.execute-api.eu-west-1.amazonaws.com/dev",
            max_workers: int = 3
            ):

        self.session = Session()
        self.session.headers.update({'x-api-key': api_key})
        self.base_url = base_url.rstrip('/')
        self.max_workers = max_workers
        self.results_queue = Queue()
        self.email_queue = Queue()

    def get_user(self, token: str) -> Dict[str, str]:
        try:
            res = self.session.get(
                url=f"{self.base_url}/userManager",
                params={'token': token}
            )
            res.raise_for_status()
            return res.json()
            
        except Exception as e:
            raise

    def _process_emails(self):
        while True:
            try:
                email = self.email_queue.get(timeout=1)
                
                try:
                    res = self.session.post(
                        url=f"{self.base_url}/insertEmail",
                        json={"email": email}
                    )
                    res.raise_for_status()
                    data = res.json()

                    token = data.get('token')
                    user_id = data.get('id')
                    
                    result = EmailResult(
                        email=email,
                        token=token,
                        user_id=user_id,
                        status='created' if token else 'error'
                    )
                    
                    if token:
                        user_data = self.get_user(token)
                        if user_data.get('email') != email:
                            result.status = 'error'
                            result.error = 'Échec de la vérification email'
                    
                    self.results_queue.put(result)
                    
                except Exception as e:
                    self.results_queue.put(EmailResult(
                        email=email,
                        status='error',
                        error=str(e)
                    ))
                
                finally:
                    self.email_queue.task_done()
                    
            except Empty:
                break

    def create_users_parallel(self, emails: List[str]) -> List[EmailResult]:        
        for email in emails:
            self.email_queue.put(email)
        
        threads = []
        for _ in range(min(self.max_workers, len(emails))):
            thread = threading.Thread(target=self._process_emails)
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        self.email_queue.join()
        
        results = []
        while not self.results_queue.empty():
            results.append(self.results_queue.get())
        
        return results

def run_tests():
    print("\nDébuts")
    test = ThreadedTEST(max_workers=3)
    test_emails = [f"testMail{i}@example.com" for i in range(3)]
    
    try:
        results = test.create_users_parallel(test_emails)
        
        successful = len([r for r in results if r.status == 'created'])
        failed = len([r for r in results if r.status == 'error'])
        
        print(f"Total emails {len(results)}")
        if successful:
            print(f"Créations ok: {successful}")
        if failed:
            print(f"Créations rate: {failed}")
        
        print("\nUtilisateurs créés:")
        for result in results:
            if result.status == 'created':
                print(f"Email : {result.email}")
                print(f"User ID : {result.user_id}")
                print(f"Token : {result.token}")
                print("---")
        
        print("terminés")
        
    except Exception as e:
        print(f"Échec: {str(e)}")
        raise

if __name__ == "__main__":
    run_tests()