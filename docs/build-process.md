# Build process

For security, performance, and cost savings, website developers started developing command line static site generators (SSGs) in 2007, with Nanoc (https://github.com/nanoc/nanoc) being one of the first. NextJS, with its innovations for building performant React sites, is currently in widespread adoption for a variety of complex sites.

In an SSG, in a local or staging environment, there is a live application running with either a database or files storing content in the background. The live application includes a server, router, templates, and front-end assets like styles, client-side scripts, and images. The application contains logic to compose HTML pages from the templates and stored content and serve them at the correct URL paths. This application has already been built for Salty SSG using FastAPI, MarkdownIT, and Jinja2. There is no SASS or React as the site only requires static CSS and Javascript.

This design document outlines the design of the command line build process used to transform the live application pages to static HTML and asset files to serve in production. I will detail the problems this process solves and its key features.

## Key problems and functionality

I will use the Textual library (https://textual.textualize.io/) to create a nice, interactive terminal experience for the Salty SSG build tool.

### 1. Source and target definition (The Where: Part I)

For any SSG, one must first define the source, in this case the domain of the local application, and the target, in this case a local file directory. The target directory can either be empty or contain some existing files for the site.

I will place these definitions in environment variables, which is typical, in order to avoid tracking them in code while making them easy to define in remote environments.

### 2. Start up the source server

The process should check if the source server is running, and if not ask the user if the tool should start it for them.

### 3. Sitemap and robots.txt generation (The What: Part I)

The SSG will need to generate the current sitemaps for the site, both for search engine ranking (SEO) purposes and for the build process itself. The basic sitemaps protocol for the public XML sitemaps is here: https://sitemaps.org/protocol.html.

The tool will create the following public sitemaps: a main-sitemap.xml for root pages, and a separate one for each subfolder's pages. These will all be located in the target root folder for simplicity. lastmod tag values will be determined from the most recent of the MD or the YML file (utility methods for this logic already exist to calculate the value for the page).

The tool will iterate on app.routes to find the path patterns to add to the sitemap. If there are any dynamic routes, the tool will query the subfolder in site/content/pages to find the dynamic paths.

Since sitemap locations are listed in robots.txt, the tool will update the sitemap URLs in the target robots.txt file as needed.

### 4. Target directory writing (The Where: Part II)

The os and shutil utilities will be used for moving and saving files to the target location.

The tool will need to, at the beginning of the build process, create all needed subfolders.

### 5. Global site updates (The What: Part II)

For design refreshes, header or footer changes, and other global updates, users will need to be able to trigger global builds, or rebuild the entire site. Global builds will be triggered via command line, similar to `next build` in NextJS.

The `route-checker` hook will run first and cancel the build if any of the expected page paths return an error response.

If the `route-checker` check passes, the tool will recursively search the site/theme/static folder for assets to copy to the target folder. (For global builds it will assume that all assets found should be copied.)

Next, the tool will visit the pages in the sitemap one by one and save the HTML from the response as an index.html file in the correct subfolder in the target folder.

Once completed, the build will log its finished time in a tracked file, src/salty_ssg/scripts/last_build_timestamp.yml.

#### Local reference scrubbing

Before the HTML is saved to the target folder during the build process, references to the local or staging domain will be scrubbed and replaced with the production domain. Because <base> tag is used with relative paths in the HTML templates, there should be minimal local domain references.

### 6. Incremental builds (The What: Part III)

(This feature has been moved to backlog as of 7/12/26.)

Incremental builds are one of the most complex aspects of any static site generator. If incremental builds are supported (a must for larger sites), the SSG must scan compiled pages and assets for changes since the last build and copy and rebuild only the pages that have changed. Strange and painful bugs can arise from the comparison logic in the incremental build process, such as time zone differences after a Daylight Savings Time change or between two environments sharing a modified timestamps manifest.

Incremental builds can be a pull or push process. For a pull process, pages are built on-demand in production when they are visited by users (see NextJS's incremental site regeneration functionality). They are then cached until cache is cleared. For a push process, the build can be run on a set schedule for sites that have many frequent small changes, or on-demand as a CI process triggered by site admins once staged changes are finalized and approved.

Here, the tool assumes a push process. There will be an extra step in the build process, to check the last modified values of the files in the site folder to make a determination of which pages and assets need to be updated in the target site.

The incremental build will be triggered by default once src/salty_ssg/scripts/last_build_timestamp.yml has been created by the first (global) build, but global builds may be triggered with a flag or terminal selection.

#### A note on assets updates

The tool assumes etags are used to ensure visitors to the live site get the latest assets for the page. This requires that server rules are added so that the user's browser will check the ETags to override cached versions of assets if necessary.

Here is an Apache example of caching and ETag rules:
```
<IfModule mod_headers.c>
    # Tell browsers to cache the file, but check the ETag every single time
    <FilesMatch "\.(css|js|svg)$">
        Header set Cache-Control "no-cache, must-revalidate"
    </FilesMatch>
</IfModule>

# Ensure ETags are on and based on content/size
FileETag MTime Size

ExpiresActive On
ExpiresByType image/jpg "access plus 1 year"
ExpiresByType image/jpeg "access plus 1 year"
ExpiresByType image/gif "access plus 1 year"
ExpiresByType image/png "access plus 1 year"
```

If more complex asset build tooling is required, it's recommended to use NodeJS tooling like Webpack and extend the scrubber utility to apply any necessary asset hashing functionality. Alternatively, an SSG built for more complex front ends like NextJS is probably preferable to Salty.
