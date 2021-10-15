#!/bin/env runhaskell

import System.FilePath
import Data.List (groupBy)

data Tree a = Leaf a | Node a [Tree a] deriving Show

instance Functor Tree where
    fmap f (Leaf x) = Leaf (f x)
    fmap f (Node dir children) = Node (f dir) (map (fmap f) children)

type FileTree = Tree FilePath
type HtmlString = String

main = do
    stylesheet <- stylesheetIO
    javascript <- javascriptIO
    tree <- readFileAsTree "toc.txt"
    let doc = makeDocument tree stylesheet javascript
    writeFile "toc.html" doc
    print $ head $ dropWhile isLeaf $ getChildren tree

isLeaf :: Tree a -> Bool
isLeaf (Leaf x) = True
isLeaf (Node x c) = False

getDir :: FileTree -> FilePath
getDir (Node dir _) = dir

getChildren :: FileTree -> [FileTree]
getChildren (Node _ children) = children

addChild :: FileTree -> FileTree -> FileTree
addChild (Node dir children) x = Node dir (x:children)

reverseChildren :: FileTree -> FileTree
reverseChildren (Node dir children) = Node dir (reverse children)

readListing :: FilePath -> IO [FilePath]
readListing = fmap lines . readFile

readFileAsTree :: FilePath -> IO FileTree
readFileAsTree = fmap (fmap (makeRelative commonPrefix) . makeTree) . readListing

makeTree :: [FilePath] -> FileTree
makeTree (root:rest) = collapse $ foldl g [Node root []] rest
  where g :: [FileTree] -> FilePath -> [FileTree]
        g (tree:stack) file =
            if takeExtension file == ""
               then if file `isChildOf` getDir tree
                       then (Node file []):tree:stack --add this folder to stack as new top tree
                       else g ((addChild (head stack) (reverseChildren tree)):(tail stack)) file --collapse top tree into second-top tree and try again
               else if file `isChildOf` getDir tree
                       then (addChild tree (Leaf file)):stack --add file to top tree's children
                       else g ((addChild (head stack) (reverseChildren tree)):(tail stack)) file
        isChildOf :: FilePath -> FilePath -> Bool
        isChildOf a b = equalFilePath (takeDirectory a) (normalise b)
        collapse :: [FileTree] -> FileTree
        collapse [tree] = reverseChildren tree
        collapse (a:b:stack) = collapse $ (addChild b a):stack

stylesheetIO :: IO String
stylesheetIO = readFile "style.css"

javascriptIO :: IO String
javascriptIO = readFile "app.js"

htmlHeader :: String -> HtmlString
htmlHeader stylesheet = "<html>\n<head>\n<title>Table of Contents</title>\n<style>" ++ stylesheet ++ "</style>\n</head>"

htmlFooter :: HtmlString
htmlFooter = "</html>"

commonPrefix :: FilePath
commonPrefix = "/mnt/c/code/github/fieldnotes-content/content"

makeHref :: FilePath -> HtmlString
makeHref file = "<a href='" ++ file ++ "'>" ++ takeFileName file ++ "</a>"

makeCollapsible :: FileTree -> HtmlString
makeCollapsible (Leaf file) = "<li>" ++ makeHref file ++ "</li>\n"
makeCollapsible (Node dir children) = "<li>" ++ dir ++ "</li>\n<ul>\n" ++ list ++ "</ul>\n"
    where list = concatMap makeCollapsible children

makeHtmlBody :: FileTree -> String -> HtmlString
makeHtmlBody filetree javascript = "<body>\n<ul id='myUL'>\n<li>\n" ++ makeCollapsible filetree ++ "</li>\n</ul>\n<script>\n" ++ javascript ++ "</script></body>"

makeDocument :: FileTree -> String -> String -> HtmlString
makeDocument dirlistings stylesheet javascript = htmlHeader "" ++ makeHtmlBody dirlistings javascript ++ htmlFooter
