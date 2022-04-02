
<h1 style="text-align:center"><a href="https://mara-li.github.io/mkdocs_obsidian_template/">PROJECT DOCUMENTATION</a></h1>

# OBSIDIAN TO MKDOCS
The script's goal is to move an authorized file (or multiple authorized file) from your Obsidian's vault to your blog's repository. It will :
- Move linked image in `docs/assets/img`
- Convert the **code block** [Admonition](https://github.com/valentine195/obsidian-admonition) to [material Admonition](https://squidfunk.github.io/mkdocs-material/reference/admonitions/)[^1]
- Convert the [Callout Syntax](https://help.obsidian.md/How+to/Use+callouts) to [material Admonition](https://squidfunk.github.io/mkdocs-material/reference/admonitions/).[^2]
- Remove Obsidian's comments as `%% comments %%`
- Copy the file in `docs` or a specific folder structure. 
- Add custom CSS based on  [markdown attribute or tags](#custom-attribute-example) ([CM6 Live Preview](https://github.com/nothingislost/obsidian-cm6-attributes) ; [Markdown Attribute](https://github.com/valentine195/obsidian-markdown-attributes) and [Contextual Typography](https://github.com/mgmeyers/obsidian-contextual-typography)). 

Furthermore, it will also carry :
- Of the support of [Folder Note — Pagination Indexes](#folder-note)
- Copy a link to the blog converted file (only if one file is converted)

## File's front matter
The script relies on the front matter** of the notes you want to publish. 
1. `share: true` allow publishing the file[^3]
2. `category` to choose where the file will be after conversion ; allowing categorization for the blog.[^4]
    - `category: false` will **hide** the file from navigation.
    - `category: hidden` will do the same.
    - `category: folder1/folder2/` will move the file in `folder2`, under `folder1`
    - `category: folder1/folder2/filename` will rename the file `index` and allow support of [section's index page](https://squidfunk.github.io/mkdocs-material/setup/setting-up-navigation/#section-index-pages)  
3. `update: false` prevent to update the file after the first publication
4. `description` : Add a description to the file (for meta-tag sharing)[^5]
5. `title` : Change the title in the navigation.
6. `image` : Add an image for meta-tags sharing.[^5] It needs to be the name of the file, as `image.png`. 

## Usage
The script can be use :
- Directly in Obsidian, using [Obsidian Shell Commands](https://github.com/Taitava/obsidian-shellcommands) (see [Obsidian Shell's configuration](#obsidian-shell-configuration))
- In [Terminal](#terminal).

The supported system are :
- macOS, Linux and Windows
- [IOS](#ios) (with [Pyto](https://pyto.app) and/or [a-shell](https://holzschu.github.io/a-Shell_iOS/) with [Working Copy](https://workingcopyapp.com/))

### Configuration
At the first run, you will be asked to configure some key and specific path.
1. <u>Vault</u> : Use the file dialog to choose your vault folder.
2. <u>Publish repository folder : </u> As vault path, use the file dialog.
3. <u>share</u> : You can change the `share` key. By default, it's `share`
4. <u>Index key:</u> Support for citation of [pagination index pages](#folder-note). By default, it uses `(i)`
5. <u>Default blog folder:</u> By default, the notes will be in `docs/notes` but you can change that, or use `/` for root. 

The file will be in `site-packages/mkdocs_obsidian/.mkdocs_obsidian` (unless for Pyto : the `.env` will be directly in `site_package/.mkdocs_obsidian`)

### Terminal 

Global options :
- `--git` : No commit and push to git ; 
- `--mobile` : Use mobile shortcuts instead of `--git`
- `--meta` : Update frontmatter of source files
- `--keep` : Don't delete files in blog folder
- `--shell` : Remove Rich printing

Commands and specific options :
- **config** : (*it will ignore `--use configuration_name`*)
    - `--new configuration_name` : Create a specific configuration for some files
- **all** : Share all vault
    - `--force` : Force updating (ignore the difference between the source and blog file)
    - `--vault` : Share all vault file, ignoring the share state.
- **`file [file*]`** : Share only one file

```bash
usage: __main__.py [-h] [--mobile | --git] [--meta] [--keep] [--use configuration_name] {config,all,file} ...

positional arguments:
  {config,all,file}
    config              Configure the script : Add or edit your vault and blog absolute path, change some keys.
    all                 Publish multiple files
    file                Publish only one file

options:
  -h, --help            show this help message and exit
  --mobile, --shortcuts
                        Use mobile shortcuts, without push
  --git, --g, --G       No commit and no push to git
  --meta, --m, --M      Update the frontmatter of the source file, adding the note blog's link
  --keep, --k, --K      Keep deleted file from vault and removed shared file
  --use configuration_name, --config configuration_name
                        Use a different config from default
```

The commands order is :
`obs2mk (global_options) [all|config|file FILEPATH] (specific_options)`
Where :
- Global and specific options are optional
- `all`, `config` and `file`[^6] are required
You can use the command without argument with `obs2mk` to share every `share: true` file in your vault.


#### Share one file : `obs2mk file FILEPATH`
It will :
- Update the `share` state in original file
- Convert one file, regardless of what is the `share` state.

#### Share all file : `obs2mk all` or `obs2mk`
You can share multiple documents at once with scanning your Vault, looking for the `share: true`. It will convert automatically these files.  
Only file with modification since the last sharing will be updated.

You can :
- Share entirely your vault (that's ignore the `share` state) with : `obs2mk all --vault`
- Ignore the difference between the source file and the blog's file with :  `obs2mk all --force`
Also, you can combine the two options. 

### Configuration
You can use and create multiple configuration files. This allows to have multiple site based on one vault, or different vault accross one site... 
1. To create a new configuration file : `obs2mk config --new configuration_name`
2. To use a configuration use : `--use configuration_name` 
    For example : `obs2mk --use configuration_name` 

[^1]: Deprecated ; Will don't be updated and be removed in future version.  
[^2]: Support nested callout :D  
[^3]: This key can be configured  
[^4]: You can customize the folder with [Awesome Pages](https://github.com/lukasgeiter/mkdocs-awesome-pages-plugin)  
[^5]: Meta tags are snippets of text that describe a page’s content; the meta tags don’t appear on the page itself, but only in the page’s source code. Meta tags are essentially little content descriptors that help tell search engines what a web page is about. *[(source)](https://www.wordstream.com/meta-tags)*  
[^6]: For `file` you need to add the filepath of the file you want to share : `obs2mk (global_option) file "filepath" (specific_options)`
