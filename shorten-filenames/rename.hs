import Control.Monad (filterM)
import System.Directory
import Data.List (isInfixOf)

main = do
    setCurrentDirectory content
    mapM_ renameSemester semesters

-- Constants
content :: FilePath
content = "/mnt/c/code/github/fieldnotes-content/content/"

semesters :: [FilePath]
semesters = ["fa14", "sp15", "fa15", "sp16", "fa16", "sp17", "sp17dh", "fa17"]

renameSemester :: FilePath -> IO ()
renameSemester semester = do
    setCurrentDirectory semester
    exists <- doesDirectoryExist "annotations"
    if exists
       then do
           renameDirectory "annotations" "ann"
           setCurrentDirectory "ann"
           folders <- getFolders
           mapM_ (\x -> renameFolder x semester "annotations" "ann") folders
           setCurrentDirectory "../"
       else return ()

    renameDirectory "fieldnotes" "fld"
    setCurrentDirectory "fld"
    folders <- getFolders
    mapM_ (\x -> renameFolder x semester "fieldnotes" "fld") folders
    setCurrentDirectory "../"

    setCurrentDirectory content

getFolders :: IO ([FilePath])
getFolders = do
    a <- listDirectory "."
    filterM (doesDirectoryExist) a

renameFolder :: FilePath -> String -> String -> String -> IO ()
renameFolder folder semester category abbrev = do
    setCurrentDirectory folder
    files <- filter (\x -> category `isInfixOf` x) <$> listDirectory "."
    mapM_ (\x -> renameFile x (replace x semester category abbrev)) files
    setCurrentDirectory "../"

replace :: FilePath -> String -> String -> String -> String
replace filename semester category abbrev = semester ++ "_" ++ abbrev ++ drop n filename
    where a = length semester
          b = length category
          n = a + b + 1
