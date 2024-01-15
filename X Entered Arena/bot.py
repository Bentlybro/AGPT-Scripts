from github import Github
import requests

g = Github("Your Github Token")

repo = g.get_repo("Significant-Gravitas/AutoGPT")

pull_requests = list(repo.get_pulls(state='open'))[::-1]

keep_open_count = 0
close_count = 0

for pr in pull_requests:
    if pr.title.endswith("entering the arena"):
        max_branches_to_check = 5
        first_word = pr.title.split()[0]
        keep_open = False

        for file in pr.get_files():
            if first_word in file.filename and file.filename.endswith(".json"):
                raw_url = file.raw_url

                response = requests.get(raw_url)
                if response.status_code == 200:
                    data = response.json()
                    github_repo_url = data.get("github_repo_url", None)

                    if github_repo_url:
                        user_repo_name = '/'.join(github_repo_url.split('/')[-2:])

                        try:
                            user_repo = g.get_repo(user_repo_name)
                            print(f"Title: {pr.title}, URL: {pr.html_url}, GitHub Repo URL: {github_repo_url}")

                            for branch in user_repo.get_branches():
                                if max_branches_to_check <= 0:
                                    break

                                branch_name = branch.name
                                comparison = repo.compare('master', f"{user_repo.owner.login}:{branch_name}")

                                if comparison.ahead_by > 0:
                                    if comparison.ahead_by > 2:
                                        keep_open = True

                                max_branches_to_check -= 1

                        except Exception as e:
                            print(f"Error accessing repository or comparing branches: {e}")
                            print(f"URL of PR with error: {pr.html_url}")

                    else:
                        print("GitHub Repo URL not found in file.")

                else:
                    print(f"Failed to fetch file: {file.filename}")

                break

        if keep_open:
            print(f"{pr.title} - Would Keep Open")
            keep_open_count += 1
        else:
            comment_message = """Thank you for your submission to enter your agent into the AutoGPT Arena. 

We're closing this PR as the associated repository has not had any new changes beyond the official repository.

We encourage you to resubmit once there are updates or new developments in your repo. Looking forward to your future contributions!"""
            
            pr.create_issue_comment(comment_message)
            pr.edit(state="closed")
            print(f"{pr.title} - Closed PR and Commented")
            close_count += 1
            

print(f"Closed: {close_count}, Kept Open: {keep_open_count}")