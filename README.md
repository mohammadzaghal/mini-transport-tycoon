# Mini Transport Tycoon Game Project

## Description
This project involves developing a simplified transportation-economic simulation game, inspired by *Transport Tycoon*, for the 2025/2026 Spring semester at ELTE Faculty of Informatics. The main goal of the game is to simulate road freight and passenger transport between cities and industrial facilities. The player will be tasked with organizing and managing a road transport network, purchasing vehicles, and maximizing profit through strategic route management.

## Team Information
- **Team Name**: 
- **Game Title**: Mini Transport Tycoon
- **Class**: Software Technology Practice, 2025/2026 Spring
- **University**: ELTE Faculty of Informatics
- **Teammates**:
  - Dana Al Tamimi
  - Mohammed Alzaghal
  - Tiya Kumar

## Technology Stack
- **Programming Language**: Python

## Core Game Features
The game is based on a 2D top-down map featuring cities, industrial facilities, and a road network. The player can build roads, place stops, purchase vehicles, define routes, and transport goods and passengers.

### Map and City Development
- **Grid-based map**: The map consists of cities and industrial facilities placed on a grid, which cannot be moved but can be connected through roads. 
- **City Growth**: Cities will expand over time, increasing in size and internal road networks. Growth will be influenced by the city's economy.
- **Roads**: Roads can be constructed on empty tiles (or after deforestation), with the primary task being to connect cities and industrial facilities.
  
### Vehicles and Routes
- **Vehicle Types**: Different vehicle types will be available (buses, trucks, and trains), each optimized for specific goods or passengers. Vehicles will have different speeds, capacities, and maintenance costs.
- **Stops and Routes**: The player can create circular routes, with vehicles automatically traveling along them. They can create stops for buses to pick up passengers. 

### Economy and Time Management
- **Initial Capital**: Players begin with a set amount of capital, and income is generated based on successful deliveries.
- **Costs**: Building roads, purchasing vehicles, and maintaining them will cost money. If the player runs out of funds, they go bankrupt and it's game over.
- **Time Speed**: The game will have multiple time speeds: pause, normal, fast (2x), and very fast (4x), allowing players to control game speed.

## Subtasks

### 1. **Forests [0.5 complexity]**
   - Trees can appear on empty tiles. There can be 1–4 trees per tile, and the number of trees may increase over time.
   - Roads can be built on forested tiles but at a higher cost for clearing.

### 2. **Rivers and Lakes [0.5 complexity]**
   - The map will feature rivers and lakes, which require bridges for transportation. There are be at least three types of bridges, each built with different materials and speed limits.

### 3. **Garage [0.5 complexity]**
   - Players can build garages for vehicle maintenance. Vehicles will return to the garage for regular maintenance, with older vehicles requiring more frequent service. Players can sell vehicles that are too old to maintain cost-effectively or purchase vehicles from here.

### 4. **City Growth [0.5 complexity]**
   - Cities grow in size over time, especially if there is regular traffic (goods or passengers). This growth will expand into adjacent tiles, forming new buildings and road networks.

### 5. **Minimap [0.5 complexity]**
   - The game map should be scrollable, and a minimap will be provided for easier navigation.

### 6. **Continuous Movement [0.5 complexity]**
   - Vehicles will move smoothly and continuously between tiles, rather than jumping from one tile to another, providing a more realistic animation.

### 7. **Map Generation [0.5 complexity]**
   - Algorithm tbd. 
   - The initial map will be generated using a procedural algorithm, such as the Wave Function Collapse algorithm, Perlin Noise, or an AI-based approach. This ensures a dynamic and varied experience for each game session.


For more details on the inspiration for this game, you can check out [OpenTTD](https://www.openttd.org/) or [OpenTTD on Steam](https://store.steampowered.com/app/1536610/OpenTTD/).

---------------------------------------------------------------------------------------------
## Getting started

To make it easy for you to get started with GitLab, here's a list of recommended next steps.

Already a pro? Just edit this README.md and make it your own. Want to make it easy? [Use the template at the bottom](#editing-this-readme)!

## Add your files

* [Create](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#create-a-file) or [upload](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) files
* [Add files using the command line](https://docs.gitlab.com/topics/git/add_files/#add-files-to-a-git-repository) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin https://szofttech.inf.elte.hu/software-technology-2026/group-10/ai-abusees.git
git branch -M master
git push -uf origin master
```

## Integrate with your tools

* [Set up project integrations](https://szofttech.inf.elte.hu/software-technology-2026/group-10/ai-abusees/-/settings/integrations)

## Collaborate with your team

* [Invite team members and collaborators](https://docs.gitlab.com/ee/user/project/members/)
* [Create a new merge request](https://docs.gitlab.com/ee/user/project/merge_requests/creating_merge_requests.html)
* [Automatically close issues from merge requests](https://docs.gitlab.com/ee/user/project/issues/managing_issues.html#closing-issues-automatically)
* [Enable merge request approvals](https://docs.gitlab.com/ee/user/project/merge_requests/approvals/)
* [Set auto-merge](https://docs.gitlab.com/user/project/merge_requests/auto_merge/)

## Test and Deploy

Use the built-in continuous integration in GitLab.

* [Get started with GitLab CI/CD](https://docs.gitlab.com/ee/ci/quick_start/)
* [Analyze your code for known vulnerabilities with Static Application Security Testing (SAST)](https://docs.gitlab.com/ee/user/application_security/sast/)
* [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://docs.gitlab.com/ee/topics/autodevops/requirements.html)
* [Use pull-based deployments for improved Kubernetes management](https://docs.gitlab.com/ee/user/clusters/agent/)
* [Set up protected environments](https://docs.gitlab.com/ee/ci/environments/protected_environments.html)

***


## Suggestions for a good README

Every project is different, so consider which of these sections apply to yours. The sections used in the template are suggestions for most open source projects. Also keep in mind that while a README can be too long and detailed, too long is better than too short. If you think your README is too long, consider utilizing another form of documentation rather than cutting out information.

## Name
Choose a self-explaining name for your project.

## Description
Let people know what your project can do specifically. Provide context and add a link to any reference visitors might be unfamiliar with. A list of Features or a Background subsection can also be added here. If there are alternatives to your project, this is a good place to list differentiating factors.

## Badges
On some READMEs, you may see small images that convey metadata, such as whether or not all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badge.

## Visuals
Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation
Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.

## Usage
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Support
Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap
If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment
Show your appreciation to those who have contributed to the project.

## License
For open source projects, say how it is licensed.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
