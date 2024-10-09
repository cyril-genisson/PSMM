# PSMM: *sous-système Python-Bash-Mariadb-Mail*

## Laboratoire de travail
### Environnement de provisionning du laboratoire
Une fois n'est pas coutume, je vais prendre le temps d'écrire rapidement un petit tutoriel pour installer
l'environnement de test à proprement parler. Nous utiliserons [Vagrant](https://www.vagrantup.com/) développé par la
société __HashiCorp__. __Vagrant__ nous permet de provisionner l'ensemble de notre laboratoire en mode _zero touch_,
on entre ainsi dans le paradigme _Infrastructure As Code_ et comme vous allez le voir ce n'est que du bonheur: une
fois que l'on y a goûté on ne peut plus s'en passer (un peu comme le s...!).

#### Installation de Vagrant et WSL
J'imagine que la majorité des étudiants de La Plateforme utilise un ordinateur portable avec un bon vieux Windows 11 Pro.
Ce n'est pas ce que je préfère ni ce que je recommande, mais parfois il faut savoir faire des compromis. La difficulté
avec Windows c'est que l'on ne peut pas installer [Ansible](https://docs.ansible.com/) dessus pour finir le provisionning.
Vous me pourriez me dire, si l'on connaît un temps soit peut Vagrant, que l'on peut parfaitement s'en passer.
Mais avouez que la tâche serait un peut plus complexe derrière. Donc, pour contourner ce manquement, nous allons mettre
un *__Pingouin dans la Fenêtre__*, pour pouvoir utiliser Ansible ultérieurement.

Commençons par l'installation de WSL et d'une distribution Linux si cela n'est pas déjà fait.
Dans un terminal PowerShell en mode Administrateur de préférence excécutons ce qui suit:
```PowerShell
wsl --install
```
et c'est tout!!!

Il ne reste plus qu'à installer un pingouin dans une fenêtre. À La Plateforme ils aiment Debian, donc c'est la
distribution que nous allons installer, mais on peut voir l'ensemble des distributions disponibles avec la commande:
```PowerShell
wsl --list -o
wsl --install --web-download Debian
```
---
*Remarque:* on préfère télécharger une distribution directement sur internet plutôt que d'installer une distribution
qu'il y a sur le Store.
---
On suit les indications pour créer son utilisateur et c'est terminé.

#### Installation de Vagrant
Pour installer Vagrant, nous avons plusieurs possibilités:
- télécharger le [MSI](https://developer.hashicorp.com/vagrant/install?product_intent=vagrant) de la dernière version
- utiliser _chocolatey_ pour ne pas avoir à quitter les doigts de notre terminal

Avec une console en mode Administrateur, pour une installation avec _chocolatey_ ([guide d'installation](https://docs.chocolatey.org/en-us/choco/setup/)):
````PowerShell
choco install vagrant
````
Et on reboot cette foutue machine.
J'imagine que tu utilises encore **VMware Workstation** pour faire tes machines virtuelles (hmm, quand vas-tu grandir?).
Allez, je ne t'en veux pas, on a tous commençait par faire des bêtises. Un jour tu changeras de système d'exploitation.
Mais pour l'heure, toujours dans une console powershell en mode administrateur:
````PowserShell
choco install vagrant-vmware-utility
````
Et enfin on installe le plugin pour la gestion du provider VMware Workstation:
```PowerShell
vagrant plugin install vagrant-vmware-desktop
```

Dans le cas où tu ulisiserais **VirtualBox** comme provider:
```PowerShell
vagrant plugin install virtualbox
```
**REMARQUE:** au moment de la rédaction de ce document, le plugin **virtualbox** ne fonctionne qu'avec **VirtualBox en version 7.0.\*** [lien de téléchargement](https://www.virtualbox.org/wiki/Download_Old_Builds_7_0).

---
**Cool? Et bien non, pas du tout!!! Il nous reste encore un peu de travail. Les prérequis sont installés donc
on peut commencer à concevoir notre laboratoire ;-).**

---

### Les contraintes
#### Réseau IPv4
|     Network      |   Gateway   |      DNS servers       |   domain name    |
|:----------------:|:-----------:|:----------------------:|:----------------:|
| 192.168.200.0/24 | 192.168.0.2 | 192.168.200.2, 8.8.8.8 | laplateforme.lan |

#### VMs à provisionner
| Host |    OS     |      IPv4      | vCPU |  RAM   | Disk |
|:----:|:---------:|:--------------:|:----:|:------:|:----:|
|  cl  | Debian 12 | 192.168.200.10 |  1   | 1024Mo | 8Go  |
| web  | Debian 12 | 192.168.200.11 |  1   | 1024Mo | 8Go  |
|  db  | Debian 12 | 192.168.200.12 |  2   | 2048Mo | 8Go  |
| ftp  | Debian 12 | 192.168.200.13 |  1   | 1024Mo | 8Go  |

#### Services actifs / Ports
| Service |   Port   |    Hosts     | Open firewall port |
|:-------:|:--------:|:------------:|:------------------:|
|   ftp   |  21/tcp  |     ftp      |        True        |
|   ssh   |  22/tcp  | web, db, ftp |        True        |
|  http   |  80/tcp  |     web      |        True        |
|  https  | 443/tcp  |     web      |        True        |
|  ftps   | 990/tcp  |     ftp      |        True        |
| mariadb | 3306/tcp |      db      |       False        |

### Création du laboratoire
Comme tu l'as compris, tout ce qui a été fait avant ne sera plus à refaire par la suite pour tes nouveaux projets.


####  Le _Vagrantfile_
TU peux consulter le code de tout ce qui suit dans le dossier [vagrant-lab](./vagrant-lab)



#### L'environnement Ansible dans WSL
Vous pouvez consulter le code source de tout ce qui suit dans le dossier [vagrant-lab](./vagrant-lab/ansible)


#### Provisionning du laboratoire
L'ensemble des scripts de provisionning se trouvent dans le répertoire [provision](./vagrant-lab/provision/).

|Script|Description|
|:-:|:-:|
| common.sh | Définit les paramètres communs à toutes les machines |
| web.sh | Définit les paramètres spécifiques à l'hôte *web* |
| ftp.sh | Définit les paramètres spécifiques à l'hôte *ftp* |
| psmm.sh | Définit les paramètres spécifiques à l'hôte *psmm* |
| actions.sh | Définit les actions à effectuer à chaque lancement de l'hôte *psmm* |

